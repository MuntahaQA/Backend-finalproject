# backend/main_app/tests/test_auth.py

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User


class AuthTests(APITestCase):

    def setUp(self):
        self.signup_url = reverse("signup")                   
        self.login_url = reverse("login")                     
        self.verify_url = reverse("token_refresh")
        self.charity_register_url = reverse(
            "charity_register")  
        self.ministry_register_url = reverse(
            "ministry_register")  

        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    # ---------- SIGNUP ----------

    def test_user_signup_success(self):
        data = {"username": "newuser", "email": "newuser@example.com",
                "password": "strongpass123"}
        res = self.client.post(self.signup_url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)
        self.assertIn("user", res.data)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    # ---------- LOGIN ----------

    def test_login_success(self):
        data = {"email": "test@example.com", "password": "testpass123"}
        res = self.client.post(self.login_url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)
        self.assertIn("user", res.data)

    def test_login_invalid_credentials(self):
        data = {"email": "test@example.com", "password": "wrong"}
        res = self.client.post(self.login_url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        data = {"email": "missing@example.com", "password": "pass"}
        res = self.client.post(self.login_url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------- VERIFY USER  ----------

    def test_verify_user_authenticated(self):
        login = self.client.post(self.login_url, {
                                 "email": "test@example.com", "password": "testpass123"}, format="json")
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        token = login.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        res = self.client.get(self.verify_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)
        self.assertIn("user", res.data)

    def test_verify_user_unauthenticated(self):
        res = self.client.get(self.verify_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------- CHARITY REGISTER  ----------

    def test_charity_registration_missing_field(self):
        data = {"email": "charity@example.com"} 
        res = self.client.post(self.charity_register_url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------- MINISTRY REGISTER  ----------

    def test_ministry_registration_missing_field(self):
        data = {"ministry_email": "ministry@example.com"}  
        res = self.client.post(self.ministry_register_url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
