# from rest_framework import status
from rest_framework import status, authentication, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate, login , logout
from .serializers import (
	UserRegistrationSerializer,
	UserAuthSerializer,
	UserChangePasswordSerializer,
	UserDetailsSerializer,
	UserSerializer
)
from .helpers import get_or_create_token, validate_email, validate_username


class UserRegistrationApiView(CreateAPIView):
	'''
	Rest Api View for User Regestration
	
	Fields:
	 	- username: The name of the user
		- password: User password
		- password_confirmation: User password confirmation

	Available Actions:
		Post: Register new user and create a new auth token
	'''
	queryset = User.objects.all()
	serializer_class = UserRegistrationSerializer

	def create(self, request, *args, **kwargs):
		response = super().create(request, *args, **kwargs)
		token = Token.objects.get(user=response.data['pk']).key
		response.data['token'] = token
		return Response(
			{
				"response": "Successfully registered new user",
				"data": response.data,
			},
			status=status.HTTP_201_CREATED
		)


class UserLoginApiView(APIView):
	'''
	Rest Api View for User Login
	
	Fields:
 		- username: The name of the user
		- password: Password for user authentication

	Available Actions:
		- Post: Login user and create a new auth token if nessesary
	'''
	serializer_class = UserAuthSerializer

	def post(self, request):
		username = request.data['username'].lower()
		password = request.data['password']
		user = authenticate(request, username=username, password=password)
		context = {}
		if user:
			login(request, user)
			token = get_or_create_token(user)
			context['response'] = 'Successfully logged in'
			context['user'] = user.username
			context['token'] = token.key
			response_status = status.HTTP_200_OK
		else:
			context['response'] = 'Error'
			context['error_message'] = 'Wrong username or password'
			response_status = status.HTTP_400_BAD_REQUEST

		return Response(context, status=response_status)


class UserLogoutApiView(APIView):
	'''
	Rest Api View for User Logout

	Available Actions:
		- Get: Logout active user and delete the auth token to force a login again
	'''
	def get(self, request, format=None):
		context = {}
		user = request.user
		if user.is_active:
			token = user.auth_token
			context['response'] = "Successfully delete token and logged out"
			context['user'] = user.username
			context['deleted_token'] = token.key
			token.delete()
			logout(request)
			response_status = status.HTTP_200_OK
		else:
			context['response'] = 'Error'
			context['error_message'] = 'No active user'
			response_status = status.HTTP_400_BAD_REQUEST
		return Response(context, status=response_status)


class ObtainAuthTokenView(APIView):
	'''
	Rest Api View for Obtain Token
	
	Fields:
 		- username: The name of the user
		- password: Password for user authentication
	
	Available Actions:
		- Post: Return existing user auth token or create a new one and return it
	'''
	serializer_class = UserAuthSerializer

	def post(self, request):
		username = request.data['username'].lower()
		password = request.data['password']
		user = authenticate(username=username, password=password)
		context = {}
		if user:
			data = {}
			token = get_or_create_token(user)
			context['response'] = 'Successfully authenticated'
			data['pk'] = user.pk
			data['username'] = user.username.lower()
			data['email'] = user.email.lower()
			data['token'] = token.key
			context['data'] = data
			response_status = status.HTTP_200_OK
		else:
			context['response'] = 'Error'
			context['error_message'] = 'Invalid credentials'
			response_status = status.HTTP_400_BAD_REQUEST

		return Response(context, status=response_status)


class UserChangePasswordApiView(UpdateAPIView):	
	'''
	Rest Api View for Change User Password

	Fields:
	 	- old_password: Old user password
		- password: New user password
		- password_confirmation: New user password confirmation
	
	Available Actions:
		- Put: Change user password if meet requirements
	'''
	serializer_class = UserChangePasswordSerializer
	model = User
	permission_classes = (IsAuthenticated,)
	authentication_classes = (SessionAuthentication, TokenAuthentication,)

	def get_object(self, queryset=None):
		obj = self.request.user
		return obj

	def update(self, request, *args, **kwargs):
		self.object = self.get_object()
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			# check old password
			if not self.object.check_password(serializer.data.get("old_password")):
				return Response(
					{"response": "Error", "error_message": "Wrong old password"}, 
					status=status.HTTP_400_BAD_REQUEST
				)
			# confirm the new passwords match
			new_password = serializer.data.get("new_password")
			confirm_new_password = serializer.data.get("confirm_new_password")
			if new_password != confirm_new_password:
				return Response(
					{"response": "Error", "error_message": "New passwords must match"}, 
					status=status.HTTP_400_BAD_REQUEST
				)
			# set_password also hashes the password that the user will get
			self.object.set_password(serializer.data.get("new_password"))
			self.object.save()
			return Response({"response":"Successfully changed password, log in with new password"}, 
				status=status.HTTP_200_OK
			)
		return Response(
					{"response": "Error", "error_message": serializer.errors}, 
					status=status.HTTP_400_BAD_REQUEST
		)


class UserDetailsApiView(APIView):
	'''
	Rest Api View for User Account Details

	Fields:
		- username: New user name(for update)
		- email: New user email(for update)
	
	Available Actions:
		- Get: Get user details
		- Put: Update username and/or user email
		- Delete: Delete user account
	'''
	serializer_class = UserDetailsSerializer
	model = User
	permission_classes = (IsAuthenticated,)
	authentication_classes = (SessionAuthentication, TokenAuthentication,)

	def get_object(self, queryset=None):
		user = self.request.user
		return user

	def get(self, request, format=None):
		user = self.get_object()
		context, data = {}, {}
		data['pk'] = user.pk
		data['username'] = user.username
		data['email'] = user.email
		token = Token.objects.get(user=user).key
		data['token'] = token
		context['response'] = 'Successfully authenticated'
		context['data'] = data
		return Response(context, status=status.HTTP_200_OK)

	def put(self, request, format=None):
		user = self.get_object()
		context = {}
		serializer = self.serializer_class(user, data=request.data, partial=True)
		if serializer.is_valid():
			data ={}
			serializer_saved = serializer.save()
			context['response'] = 'Successfully update'
			data['pk'] = user.pk
			data['email'] = serializer_saved.email.lower()
			data['username'] = serializer_saved.username.lower()
			token = Token.objects.get(user=user).key
			data['token'] = token
			context['data'] = data
			response_status = status.HTTP_200_OK
		else:
			context['response'] = 'Error'
			context['error_message'] = serializer.errors
			response_status = status.HTTP_400_BAD_REQUEST
		return Response(context, response_status)

	def delete(self, request, format=None):
		user = self.get_object()
		user.delete()
		return Response({'response': 'Successfully deleted'}, status=status.HTTP_204_NO_CONTENT)


class UserListApiView(ListAPIView):
	"""
	Rest List Api View for Users
	
	Fields:
		- pk : The user primary key
		- username: The user acount name
		- email: The user email
		- token: The user current token or blank
	
	Requirements:
		Super User Account
	"""
	permission_classes = (IsAdminUser,)
	queryset = User.objects.all().order_by('-date_joined')
	serializer_class = UserSerializer