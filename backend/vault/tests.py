from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.sessions.middleware import SessionMiddleware
from rest_framework import status
from rest_framework.test import APITestCase
from app.models import Organization, Department, User, AdminConfig
from vault.models import VaultItem, AuditEvent

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

        # Valid token should not 404 (might redirect to login or show admin)
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
            target_id="unauthorized",
            metadata__reason="invalid_or_expired_token"
        ).exists())
