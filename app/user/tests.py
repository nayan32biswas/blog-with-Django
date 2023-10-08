from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()

print("Discover test")


class UserAuthTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            "username": "demousername",
            "password": "demopassword",
            "full_name": "User Name",
        }
        self.base_user = User.objects.create_user(**self.user_data)  # type: ignore
        self.client = APIClient()

    def test_registration(self):
        url = "/api/v1/registration/"
        payload = {
            **self.user_data,
            "username": "change",
        }
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        """Test Duplicate username """
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login(self):
        url = "/api/v1/token/"
        payload = {
            "username": self.user_data["username"],
            "password": self.user_data["password"],
        }
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        """Test With worong credintial"""
        payload["password"] = "unknownpassword"
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile(self):
        url = "/api/v1/me/"
        self.client.force_authenticate(user=self.base_user)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_profile(self):
        url = "/api/v1/me/"
        self.client.force_authenticate(user=self.base_user)
        payload = {"full_name": "Change"}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = self.base_user
        user.refresh_from_db()
        self.assertEqual(payload["full_name"], user.full_name)

    def test_change_password(self):
        url = "/api/v1/change-password/"
        self.client.force_authenticate(user=self.base_user)
        payload = {
            "current_password": self.user_data["password"],
            "new_password": "changepassword",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = self.base_user
        user.refresh_from_db()
        self.assertTrue(user.check_password(payload["new_password"]))

    def test_public_user(self):
        user = User.objects.first()
        url = f"/api/v1/users/{user.username}/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
