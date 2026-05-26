from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from app.models import Organization, Department, User
from vault.models import VaultItem

class MFASecurityTests(APITestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Security Org", slug="sec-org")
        self.user = User.objects.create_user(
            username="mfauser",
            password="password",
            organization=self.org,
            mfa_enabled=True
        )
        self.item = VaultItem.objects.create(
            owner=self.user,
            organization=self.org,
            scope=VaultItem.Scope.PERSONAL,
            title="MFA Protected Secret",
            encrypted_blob=b"data",
            nonce=b"nonce"
        )

    def test_mfa_enabled_user_cannot_access_without_verification(self):
        """A user with MFA enabled should not be able to access vault items if they haven't verified MFA."""
        self.client.force_login(self.user)
        # Manually set last_login to now, and last_mfa_login to None or older
        self.user.last_login = timezone.now()
        self.user.last_mfa_login = None
        self.user.save()

        url = reverse("vault-item-list")
        response = self.client.get(url)

        # Currently, this will likely return 200 because MFA is not enforced in the API
        # We want it to return 403 or an empty list (depending on implementation)
        # For a security agent, 403 Forbidden or 401 Unauthorized is better for sensitive data.
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

    def test_mfa_verified_user_can_access(self):
        """A user with MFA enabled can access items after verification."""
        self.client.force_login(self.user)
        self.user.last_login = timezone.now()
        self.user.last_mfa_login = timezone.now() + timezone.timedelta(seconds=1)
        self.user.save()

        url = reverse("vault-item-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
