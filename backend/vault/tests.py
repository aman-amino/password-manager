from datetime import timedelta
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from app.models import Organization, Department, User, AdminConfig
from vault.models import VaultItem, AuditEvent, AccessGrant

class VaultItemPolicyTests(APITestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Test Org", slug="test-org")
        self.dept = Department.objects.create(organization=self.org, name="Test Dept", slug="test-dept")

        self.superadmin = User.objects.create_user(
            username="superadmin", password="password", role=User.Role.SUPERADMIN
        )
        self.admin = User.objects.create_user(
            username="admin", password="password", role=User.Role.ADMIN, organization=self.org
        )
        self.user = User.objects.create_user(
            username="user", password="password", role=User.Role.USER, organization=self.org, department=self.dept
        )

        self.personal_item = VaultItem.objects.create(
            owner=self.user, organization=self.org, department=self.dept,
            scope=VaultItem.Scope.PERSONAL, title="Personal Secret",
            encrypted_blob=b"data", nonce=b"nonce"
        )
        self.org_item = VaultItem.objects.create(
            owner=self.admin, organization=self.org,
            scope=VaultItem.Scope.ORG, title="Org Secret",
            encrypted_blob=b"data", nonce=b"nonce"
        )

    def test_superadmin_visibility(self):
        """Superadmin should see org items but not other's personal items."""
        self.client.force_authenticate(user=self.superadmin)
        url = reverse("vault-item-list")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data]
        self.assertIn(self.org_item.id, ids)
        self.assertNotIn(self.personal_item.id, ids)

    def test_user_visibility(self):
        """User should see their own personal items and relevant scoped items."""
        self.client.force_authenticate(user=self.user)
        url = reverse("vault-item-list")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data]
        self.assertIn(self.personal_item.id, ids)
        # Org items are visible to all in org unless explicitly restricted,
        # but our policy says regular users only see owner or grants.
        self.assertNotIn(self.org_item.id, ids)

    def test_audit_logging(self):
        """Audit events should be logged on access."""
        self.client.force_authenticate(user=self.user)
        url = reverse("vault-item-detail", args=[self.personal_item.id])
        self.client.get(url, follow=True)

        self.assertTrue(AuditEvent.objects.filter(
            actor=self.user,
            action=AuditEvent.Action.READ,
            target_id=str(self.personal_item.id)
        ).exists())

class AdminRotationTests(APITestCase):
    def setUp(self):
        self.superadmin = User.objects.create_user(
            username="superadmin", password="password", role=User.Role.SUPERADMIN
        )

    def test_rotate_admin_url_post(self):
        self.superadmin.is_staff = True
        self.superadmin.is_superuser = True
        self.superadmin.save()
        self.client.force_login(user=self.superadmin)
        url = reverse("rotate_admin")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("admin_url", data)
        token = data["admin_url"].split("_")[1].strip("/")
        self.assertTrue(AdminConfig.objects.filter(admin_token__startswith=token, is_active=True).exists())

    def test_rotate_admin_url_get_fails(self):
        self.client.force_login(user=self.superadmin)
        url = reverse("rotate_admin")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_admin_middleware_protection(self):
        # Create an active token
        AdminConfig.objects.create(admin_token="secret-token", is_active=True)

        # Valid token should not 404 for superadmin
        superadmin = User.objects.create_user(username="adm", password="pwd", role=User.Role.SUPERADMIN)
        self.client.force_login(user=superadmin)
        response = self.client.get("/admin_secret-token/")
        self.assertNotEqual(response.status_code, 404)

        # Invalid token should 404
        response = self.client.get("/admin_wrong-token/")
        self.assertEqual(response.status_code, 404)

class SecurityAuditLoggingTests(APITestCase):
    def setUp(self):
        self.superadmin = User.objects.create_user(
            username="superadmin", password="password", role=User.Role.SUPERADMIN
        )
        self.user = User.objects.create_user(
            username="testuser", password="password", role=User.Role.USER
        )

    def test_login_audit_logging(self):
        """Successful login should be logged."""
        factory = RequestFactory()
        request = factory.post('/login/')

        # Add session
        middleware = SessionMiddleware(lambda r: None)
        middleware.process_request(request)
        request.session.save()

        user = authenticate(request, username='testuser', password='password')
        request.user = user
        login(request, user)

        self.assertTrue(AuditEvent.objects.filter(
            actor=self.user,
            action=AuditEvent.Action.LOGIN,
            target_type="user",
            target_id=str(self.user.id)
        ).exists())

    def test_rotate_admin_audit_logging(self):
        """Admin URL rotation should be logged."""
        self.client.force_login(user=self.superadmin)
        url = reverse("rotate_admin")
        self.client.post(url)

        self.assertTrue(AuditEvent.objects.filter(
            actor=self.superadmin,
            action=AuditEvent.Action.ADMIN,
            metadata__action="rotate_admin_url"
        ).exists())

    def test_unauthorized_admin_audit_logging(self):
        """Unauthorized admin access should be logged."""
        # Create an active token so the middleware doesn't bypass
        AdminConfig.objects.create(admin_token="valid-token", is_active=True)

        # Access with invalid token
        self.client.get("/admin_invalid-token/")

        self.assertTrue(AuditEvent.objects.filter(
            action=AuditEvent.Action.ADMIN,
            target_type="admin_access",
            target_id="unauthorized_token",
            metadata__reason="invalid_or_expired_token"
        ).exists())

class AccessGrantExpirationTests(APITestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Exp Org", slug="exp-org")
        self.user_a = User.objects.create_user(
            username="userA", password="password", role=User.Role.USER, organization=self.org
        )
        self.user_b = User.objects.create_user(
            username="userB", password="password", role=User.Role.USER, organization=self.org
        )
        self.item = VaultItem.objects.create(
            owner=self.user_a, organization=self.org,
            scope=VaultItem.Scope.PERSONAL, title="Shared Secret",
            encrypted_blob=b"data", nonce=b"nonce"
        )

    def test_active_unexpired_grant_allowed(self):
        """Active and unexpired grant should allow access."""
        future = timezone.now() + timedelta(days=1)
        AccessGrant.objects.create(
            vault_item=self.item, grantee=self.user_b, granted_by=self.user_a,
            is_active=True, expires_at=future
        )
        self.client.force_authenticate(user=self.user_b)
        url = reverse("vault-item-detail", args=[self.item.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_expired_grant_denied(self):
        """Expired grant should deny access even if is_active is True."""
        past = timezone.now() - timedelta(days=1)
        AccessGrant.objects.create(
            vault_item=self.item, grantee=self.user_b, granted_by=self.user_a,
            is_active=True, expires_at=past
        )
        self.client.force_authenticate(user=self.user_b)
        url = reverse("vault-item-detail", args=[self.item.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class SubadminEscalationTests(APITestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Sub Org", slug="sub-org")
        self.dept = Department.objects.create(organization=self.org, name="Sub Dept", slug="sub-dept")
        self.admin = User.objects.create_user(
            username="orgadmin", password="password", role=User.Role.ADMIN, organization=self.org
        )
        self.subadmin = User.objects.create_user(
            username="subadmin", password="password", role=User.Role.SUBADMIN,
            organization=self.org, department=self.dept
        )
        self.org_item = VaultItem.objects.create(
            owner=self.admin, organization=self.org, department=self.dept,
            scope=VaultItem.Scope.ORG, title="Org Wide Secret",
            encrypted_blob=b"data", nonce=b"nonce"
        )
        self.dept_item = VaultItem.objects.create(
            owner=self.admin, organization=self.org, department=self.dept,
            scope=VaultItem.Scope.DEPT, title="Dept Only Secret",
            encrypted_blob=b"data", nonce=b"nonce"
        )

    def test_subadmin_sees_dept_item(self):
        """Subadmin should see DEPT scoped items in their department."""
        self.client.force_authenticate(user=self.subadmin)
        url = reverse("vault-item-list")
        response = self.client.get(url, follow=True)
        ids = [item["id"] for item in response.data]
        self.assertIn(self.dept_item.id, ids)

    def test_subadmin_cannot_see_org_item(self):
        """Subadmin should NOT see ORG scoped items in their department unless granted."""
        self.client.force_authenticate(user=self.subadmin)
        url = reverse("vault-item-list")
        response = self.client.get(url, follow=True)
        ids = [item["id"] for item in response.data]
        self.assertNotIn(self.org_item.id, ids)

class AdminRoleRestrictionTests(APITestCase):
    def setUp(self):
        self.superadmin = User.objects.create_user(
            username="superadmin", password="password", role=User.Role.SUPERADMIN
        )
        self.staff_user = User.objects.create_user(
            username="staff", password="password", role=User.Role.USER, is_staff=True
        )
        self.token = "valid-token"
        AdminConfig.objects.create(admin_token=self.token, is_active=True)

    def test_superadmin_access_allowed(self):
        """Superadmin should be allowed with valid token."""
        self.client.force_login(user=self.superadmin)
        response = self.client.get(f"/admin_{self.token}/")
        self.assertNotEqual(response.status_code, 404)

    def test_non_superadmin_staff_denied(self):
        """Staff user who is NOT a superadmin should be denied access."""
        self.client.force_login(user=self.staff_user)
        response = self.client.get(f"/admin_{self.token}/")
        self.assertEqual(response.status_code, 404)

class SuperadminPersonalGrantTests(APITestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Super Org", slug="super-org")
        self.superadmin = User.objects.create_user(
            username="superadmin_grant", password="password", role=User.Role.SUPERADMIN
        )
        self.user = User.objects.create_user(
            username="user_owner", password="password", role=User.Role.USER, organization=self.org
        )
        self.personal_item = VaultItem.objects.create(
            owner=self.user, organization=self.org,
            scope=VaultItem.Scope.PERSONAL, title="Super Secret",
            encrypted_blob=b"data", nonce=b"nonce"
        )

    def test_superadmin_list_sees_granted_personal_item(self):
        """Superadmin should see a personal item in list view IF granted access."""
        # Before grant, should NOT see
        self.client.force_authenticate(user=self.superadmin)
        url = reverse("vault-item-list")
        response = self.client.get(url, follow=True)
        ids = [item["id"] for item in response.data]
        self.assertNotIn(self.personal_item.id, ids)

        # After grant, SHOULD see
        AccessGrant.objects.create(
            vault_item=self.personal_item, grantee=self.superadmin,
            granted_by=self.user, is_active=True
        )
        response = self.client.get(url, follow=True)
        ids = [item["id"] for item in response.data]
        self.assertIn(self.personal_item.id, ids)

class AuditLogRedactionTests(APITestCase):
    def test_admin_token_redaction_in_logs(self):
        """Secret admin tokens should be redacted in audit log metadata."""
        token = "secret-token-123"
        AdminConfig.objects.create(admin_token=token, is_active=True)

        # Access with invalid token (trigger middleware log)
        self.client.get("/admin_wrong-token/")

        # Verify log entry exists and is redacted
        log = AuditEvent.objects.filter(target_id="unauthorized_token").latest('created_at')
        self.assertIn("[REDACTED]", log.metadata["path"])
        self.assertNotIn("wrong-token", log.metadata["path"])
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

class PasswordPolicyTests(TestCase):
    def test_weak_passwords_fail(self):
        """Weak passwords should fail complexity validation."""
        weak_passwords = [
            "short1!",       # too short
            "alllowercase1!", # no uppercase
            "ALLUPPERCASE1!", # no lowercase
            "NoDigitSpecial", # no digit, no special
            "NoSpecial1",     # no special
        ]
        for password in weak_passwords:
            with self.subTest(password=password):
                with self.assertRaises(ValidationError):
                    validate_password(password)

    def test_strong_password_passes(self):
        """A strong password meeting all criteria should pass."""
        strong = "StrongPass123!"
        try:
            validate_password(strong)
        except ValidationError:
            self.fail("Strong password failed validation!")

class MFAEnforcementTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="mfauser", password="StrongPass123!", mfa_enabled=True
        )

    def test_mfa_enabled_user_denied_without_verification(self):
        """User with MFA enabled should be denied access if mfa_verified is not in session."""
        self.client.force_login(user=self.user)
        url = reverse("vault-item-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"error": "MFA verification required"})

    def test_mfa_enabled_user_allowed_after_verification(self):
        """User with MFA enabled should be allowed if mfa_verified is in session."""
        self.client.force_login(user=self.user)
        # Manually inject session data
        session = self.client.session
        session['mfa_verified'] = True
        session.save()

        url = reverse("vault-item-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_mfa_disabled_user_always_allowed(self):
        """User with MFA disabled should not be affected by the middleware."""
        user_no_mfa = User.objects.create_user(
            username="nomfa", password="StrongPass123!", mfa_enabled=False
        )
        self.client.force_login(user=user_no_mfa)
        url = reverse("vault-item-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
