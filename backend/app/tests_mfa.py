import pyotp
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from app.models import User

class MFASecurityTests(APITestCase):
    def setUp(self):
        self.secret = pyotp.random_base32()
        self.user = User.objects.create_user(
            username="testuser",
            password="password",
            totp_secret=self.secret,
            mfa_enabled=True
        )
        self.client.force_login(self.user)
        self.url = reverse("verify_mfa")

    def test_verify_mfa_success(self):
        """Valid TOTP code should succeed."""
        totp = pyotp.TOTP(self.secret)
        code = totp.now()
        response = self.client.post(self.url, {"code": code})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], "success")

        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_mfa_login)

    def test_verify_mfa_failure_invalid_code(self):
        """Invalid TOTP code should fail."""
        response = self.client.post(self.url, {"code": "000000"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["status"], "error")

    def test_verify_mfa_failure_hardcoded_code(self):
        """The old hardcoded code '123456' should no longer work (unless it happens to be valid)."""
        # It's extremely unlikely '123456' is the current code for a random secret
        response = self.client.post(self.url, {"code": "123456"})
        # We check for 403, but if by some miracle it's valid, the test might fail.
        # Given 10^6 possibilities, it's 1 in a million.
        if response.status_code == 200:
             # Try again with a different secret if we hit the jackpot
             self.secret = pyotp.random_base32()
             self.user.totp_secret = self.secret
             self.user.save()
             response = self.client.post(self.url, {"code": "123456"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_verify_mfa_no_secret(self):
        """User without MFA setup should fail."""
        self.user.totp_secret = None
        self.user.save()
        response = self.client.post(self.url, {"code": "123456"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
