from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from unittest.mock import patch


class RegistrationTestCase(APITestCase):

	@classmethod
	def setUpClass(cls):
		super(RegistrationTestCase,cls).setUpClass()
		User.objects.create_user(username="TestUser",
								 email="testuser@email.com",
		                         password="some_strong_psw")

	def test_registration(self):
		data = {"username": "NewTestUser", "email": "newtestuser@email.com",
				"password": "some_strong_psw", "password_confirmation": "some_strong_psw"}
		response = self.client.post("/api/users/register/", data)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_user_exists(self):
		data = {"username": "TestUser", "email": "newtestuser@email.com",
				"password": "some_strong_psw", "password_confirmation": "some_strong_psw"}
		response = self.client.post("/api/users/register/", data)
		expected_response = {"username": ["A user with that username already exists."] }
		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_email_exists(self):
		data = {"username": "NewTestUser", "email": "testuser@email.com",
				"password": "some_strong_psw", "password_confirmation": "some_strong_psw"}
		response = self.client.post("/api/users/register/", data)
		expected_response = {"response": ["Email testuser@email.com is already in use."] }
		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_wrong_passwords(self):
		data = {"username": "NewTestUser", "email": "newtestuser@email.com",
				"password": "some_strong_psw", "password_confirmation": "wrong_some_strong_psw"}
		response = self.client.post("/api/users/register/", data)
		expected_response = {"response": ["Passwords must match"] }
		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTestCase(APITestCase):

	def setUp(self):
		self.user = User.objects.create(username="testuser",
		                         		password="some_strong_psw")
		self.token = Token.objects.get(user=self.user).key

	@patch('Users.api.views.authenticate')
	def test_login(self, mock_authenticate):
		mock_authenticate.return_value = self.user
		data = {"username": "testuser", "password": "some_strong_psw"}
		response = self.client.post("/api/users/login/", data)
		expected_response = {
			"response": "Successfully logged in",
    		"user": self.user.username,
    		"token": self.token
		}
		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	@patch('Users.api.views.authenticate')
	def test_wrong_input(self, mock_authenticate):
		mock_authenticate.return_value = None
		data = {"username": "FakeUser", "password": "some_strong_psw"}
		response = self.client.post("/api/users/login/", data)
		expected_response = {"response": "Error", "error_message": "Wrong username or password"}
		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutTestCase(APITestCase):

	def setUp(self):
		self.user = User.objects.create(username="testuser",
										email="testuser@email.com",
		                         		password="some_strong_psw")
		self.token = Token.objects.get(user=self.user).key

	def test_logout(self):
		self.client.force_authenticate(user=self.user)
		response = self.client.get("/api/users/logout/")
		expected_response =	{
	    	"response": "Successfully delete token and logged out",
	    	"user": self.user.username,
	    	"deleted_token": self.token,
		}
		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_no_active_user(self):
		response = self.client.get("/api/users/logout/")
		expected_response =	{
    		"response": "Error",
    		"error_message": "No active user"
		}
		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ObtainAuthTokenTestCase(APITestCase):

	def setUp(self):
		self.user = User.objects.create(username="testuser",
										email="testuser@email.com",
		                         		password="some_strong_psw")
		self.token = Token.objects.get(user=self.user).key

	@patch('Users.api.views.authenticate')
	def test_obtain_token(self, mock_authenticate):
		mock_authenticate.return_value = self.user
		data = {"username": "testuser", "password": "some_strong_psw"}
		response = self.client.post("/api/users/token-auth/", data)
		expected_response = {
    		"response": "Successfully authenticated",
		    "data": {
		        "pk": self.user.pk,
		        "username": self.user.username,
		        "email": self.user.email,
		        "token": self.token
		    }
		}
		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	@patch('Users.api.views.authenticate')
	def test_wrong_input(self, mock_authenticate):
		mock_authenticate.return_value = None
		data = {"username": "FakeUser", "password": "some_strong_psw"}
		response = self.client.post("/api/users/token-auth/", data)
		expected_response = {
    		"response": "Error",
    		"error_message": "Invalid credentials"
		}
		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ChangePasswordTestCase(APITestCase):

	def setUp(self):
		self.user = User.objects.create_user(username="testuser",
											 email="testuser@email.com",
		                         			 password="some_strong_psw")
		self.client.force_authenticate(user=self.user)

	def test_change_password(self):
		data = {
			"old_password": "some_strong_psw", 
			"new_password": "new_strong_psw",
			"confirm_new_password": "new_strong_psw",
		}
		response = self.client.put("/api/users/change-password/", data)
		expected_response = { "response": "Successfully changed password, log in with new password" }
		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_wrong_old_password(self):
		data = {
			"old_password": "wrong_strong_psw", 
			"new_password": "new_strong_psw",
			"confirm_new_password": "new_strong_psw",
		}
		response = self.client.put("/api/users/change-password/", data)
		expected_response = {
		    "response": "Error",
		    "error_message": "Wrong old password"
		}
		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_wrong_password_confirmation(self):
		data = {
			"old_password": "some_strong_psw", 
			"new_password": "new_strong_psw",
			"confirm_new_password": "wrong_strong_psw",
		}
		response = self.client.put("/api/users/change-password/", data)
		expected_response = {
    		"response": "Error",
    		"error_message": "New passwords must match"
		}
		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserDetailsTestCase(APITestCase):

	def setUp(self):
		self.user = User.objects.create_user(username="testuser",
											 email="testuser@email.com",
		                         			 password="some_strong_psw")
		self.user_2 = User.objects.create_user(username="testuser2",
											   email="testuser2@email.com",
		                         			   password="some_strong_psw")
		self.token = Token.objects.get(user=self.user).key
		self.client.force_authenticate(user=self.user)

	def test_get(self):
		response = self.client.get("/api/users/user-details/")
		expected_response = {
			"response": "Successfully authenticated",
			"data": {
			    "pk": self.user.pk,
			    "username": self.user.username,
			    "email": self.user.email,
			    "token": self.token
			}
		}
		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_put(self):
		data = {
				"username": "newuser",
				"email": "newuser@email.com",
		}
		response = self.client.put("/api/users/user-details/", data)
		expected_response = {
		    "response": "Successfully update",
		    "data": {
		        "pk": self.user.pk,
		        "email": self.user.email,
		        "username": self.user.username,
		        "token": self.token
		    }
		}
		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(data['username'], self.user.username)
		self.assertEqual(data['email'], self.user.email)

	def test_email_exists(self):
		data = {
				"username": "newuser",
				"email": "testuser2@email.com",
		}
		response = self.client.put("/api/users/user-details/", data)
		expected_response = {
    		"response": "Error",
    		"error_message": {
        		"email": [
            				"A user with that email already exist"
        		]		
    		}
		}
		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_user_exists(self):
		data = {
				"username": "testuser2",
				"email": "newuser@email.com",
		}
		response = self.client.put("/api/users/user-details/", data)
		expected_response = {
    		"response": "Error",
    		"error_message": {
		        "username": [
		            "A user with that username already exists."
		        ]	
    		}
		}
		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_delete(self):
		response = self.client.delete("/api/users/user-details/")
		expected_response = {
    		"response": "Successfully deleted"
		}			
		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(User.objects.count(), 1)


class UserListTestCase(APITestCase):

	def setUp(self):
		self.user = User.objects.create_user(username="testuser",
											 email="testuser@email.com",
		                         			 password="some_strong_psw")
		self.user_2 = User.objects.create_user(username="testuser2",
											   email="testuser2@email.com",
		                         			   password="some_strong_psw")
		
	def test_get(self):
		self.user.is_staff = True
		self.client.force_authenticate(user=self.user)

		response = self.client.get("/api/users/user-list/")
		self.assertEqual(response.data['count'], User.objects.count())
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_no_credential(self):
		self.client.force_authenticate(user=self.user)

		response = self.client.get("/api/users/user-list/")
		expected_response = {
    		"detail": "You do not have permission to perform this action."
		}
		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)