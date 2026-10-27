from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserAuthTests(APITestCase):
    def setUp(self):
        self.register_url = "/api/v1/user/register/"
        self.login_url = "/api/v1/login/"
        self.logout_url = "/api/v1/logout/"
        self.profile_url = "/api/v1/user/profile/"
        self.refresh_url = "/api/v1/refresh-token/"

        self.user_data = {
            "email": "testuser@example.com",
            "password": "Password123!",
            "first_name": "John",
            "last_name": "Doe",
        }

    def test_register_user_success(self):
        res = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["email"], self.user_data["email"])
        self.assertNotIn("password", res.data)

        # check user in db & password hashed
        user = User.objects.get(email=self.user_data["email"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertEqual(user.token_version, 1)

    def test_register_duplicate_email_fails(self):
        self.client.post(self.register_url, self.user_data, format="json")
        res = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        self.client.post(self.register_url, self.user_data, format="json")
        res = self.client.post(
            self.login_url,
            {"email": self.user_data["email"], "password": self.user_data["password"]},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("token", res.data)
        self.assertIn("access", res.data["token"])
        self.assertIn("refresh", res.data["token"])

    def test_login_wrong_password_fails(self):
        self.client.post(self.register_url, self.user_data, format="json")
        res = self.client.post(
            self.login_url,
            {"email": self.user_data["email"], "password": "wrongpassword"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_requires_authentication(self):
        # unauthenticated should fail with 401
        res = self.client.get(self.profile_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_authenticated_success(self):
        self.client.post(self.register_url, self.user_data, format="json")
        login_res = self.client.post(
            self.login_url,
            {"email": self.user_data["email"], "password": self.user_data["password"]},
            format="json",
        )
        token = login_res.data["token"]["access"]

        # test GET profile
        res = self.client.get(self.profile_url, HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.user_data["email"])

    def test_logout_invalidates_access_token_immediately(self):
        # 1. register & login
        self.client.post(self.register_url, self.user_data, format="json")
        login_res = self.client.post(
            self.login_url,
            {"email": self.user_data["email"], "password": self.user_data["password"]},
            format="json",
        )
        access_token = login_res.data["token"]["access"]
        refresh_token = login_res.data["token"]["refresh"]

        # 2. confirm token works before logout
        res_before = self.client.get(self.profile_url, HTTP_AUTHORIZATION=f"Bearer {access_token}")
        self.assertEqual(res_before.status_code, status.HTTP_200_OK)

        # 3. logout
        logout_res = self.client.post(
            self.logout_url,
            {"refresh": refresh_token},
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            format="json",
        )
        self.assertEqual(logout_res.status_code, status.HTTP_200_OK)

        # 4. the same access token MUST now return 401
        res_after = self.client.get(self.profile_url, HTTP_AUTHORIZATION=f"Bearer {access_token}")
        self.assertEqual(res_after.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        self.client.post(self.register_url, self.user_data, format="json")
        login_res = self.client.post(
            self.login_url,
            {"email": self.user_data["email"], "password": self.user_data["password"]},
            format="json",
        )
        refresh_token = login_res.data["token"]["refresh"]

        # refresh token
        refresh_res = self.client.post(self.refresh_url, {"refresh": refresh_token}, format="json")
        self.assertEqual(refresh_res.status_code, status.HTTP_200_OK)
        new_access_token = refresh_res.data["token"]["access"]

        # new access token should work
        profile_res = self.client.get(self.profile_url, HTTP_AUTHORIZATION=f"Bearer {new_access_token}")
        self.assertEqual(profile_res.status_code, status.HTTP_200_OK)

