from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from app.models import User, Organization
import base64

class ZKAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.me_url = reverse('me')

    def test_registration_and_login_flow(self):
        # Register
        reg_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "authkey_derived_on_client",
            "salt": base64.b64encode(b"salt").decode(),
            "iterations": 100000,
            "encrypted_user_key": base64.b64encode(b"nonce.encrypted_key").decode()
        }
        response = self.client.post(self.register_url, reg_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Login
        login_data = {
            "username": "testuser",
            "password": "authkey_derived_on_client"
        }
        response = self.client.post(self.login_url, login_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Me
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['username'], 'testuser')

class VaultTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Test Org", slug="test-org")
        self.user = User.objects.create_user(username="vaultuser", password="password", organization=self.org)
        self.client.force_login(self.user)
        self.vault_url = "/api/vault-items/"

    def test_create_vault_item(self):
        data = {
            "title": "Secret 1",
            "item_type": "password",
            "scope": "personal",
            "encrypted_blob": base64.b64encode(b"encrypted").decode(),
            "nonce": base64.b64encode(b"nonce1234567").decode()
        }
        response = self.client.post(self.vault_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['title'], 'Secret 1')
