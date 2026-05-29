from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from app.models import Organization, User
from vault.models import VaultItem, AccessGrant, AuditEvent

class AccessGrantIDORTests(APITestCase):
    def setUp(self):
        self.org1 = Organization.objects.create(name="Org 1", slug="org1")
        self.org2 = Organization.objects.create(name="Org 2", slug="org2")

        self.user1 = User.objects.create_user(username="user1", password="password", organization=self.org1)
        self.user2 = User.objects.create_user(username="user2", password="password", organization=self.org2)

        self.item1 = VaultItem.objects.create(
            owner=self.user1,
            organization=self.org1,
            scope=VaultItem.Scope.PERSONAL,
            title="User 1 Private Secret",
            encrypted_blob=b"data",
            nonce=b"nonce"
        )

    def test_user_cannot_grant_access_to_item_they_dont_own(self):
        """
        VULNERABILITY: An attacker (user2) can grant access to user1's private item to themselves.
        """
        self.client.force_login(self.user2)
        url = reverse("access-grant-list")
        data = {
            "vault_item": self.item1.id,
            "grantee_username": self.user2.username
        }

        response = self.client.post(url, data, format='json')

        # This SHOULD fail with 403 or 400 validation error
        # Serializer validation returns 400.
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN])

class AuditEventLeakTests(APITestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Leak Org", slug="leak-org")
        self.admin = User.objects.create_user(username="admin", password="password", organization=self.org, role=User.Role.ADMIN)
        self.user = User.objects.create_user(username="user", password="password", organization=self.org, role=User.Role.USER)

        # Admin action
        AuditEvent.objects.create(
            actor=self.admin,
            organization=self.org,
            target_type="system",
            target_id="1",
            action=AuditEvent.Action.ADMIN,
            metadata={"secret": "admin-info"}
        )

    def test_regular_user_cannot_see_org_audit_logs(self):
        """
        VULNERABILITY: Regular users can see all audit logs for their organization.
        """
        self.client.force_login(self.user)
        url = reverse("audit-event-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Regular user should only see 0 logs (or only their own if they had any)
        # Currently they see the admin log because of the queryset logic in AuditEventViewSet
        self.assertEqual(len(response.data), 0)
