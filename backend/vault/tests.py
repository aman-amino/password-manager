from django.test import TestCase
from django.urls import reverse
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

    def test_rotate_admin_url(self):
        self.superadmin.is_staff = True
        self.superadmin.is_superuser = True
        self.superadmin.save()
        self.client.force_login(user=self.superadmin)
        url = reverse("rotate_admin")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("admin_url", data)
        token = data["admin_url"].split("_")[1].strip("/")
        self.assertTrue(AdminConfig.objects.filter(admin_token__startswith=token, is_active=True).exists())

    def test_admin_middleware_protection(self):
        # Create an active token
        AdminConfig.objects.create(admin_token="secret-token", is_active=True)

        # Valid token should not 404 (might redirect to login or show admin)
        response = self.client.get("/admin_secret-token/")
        self.assertNotEqual(response.status_code, 404)

        # Invalid token should 404
        response = self.client.get("/admin_wrong-token/")
        self.assertEqual(response.status_code, 404)
