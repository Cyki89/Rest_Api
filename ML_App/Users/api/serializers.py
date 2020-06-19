from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import (
	Serializer,
	ModelSerializer,
	ValidationError,
	SerializerMethodField,
)
from rest_framework.authtoken.models import Token
from .helpers import validate_email, validate_username


class UserAuthSerializer(ModelSerializer):
	'''
	Serializer for User Authenticate

	Fields:
	 	username: The name of the user.
		password: The passwrod for user authentication.
	'''
	class Meta:
		model = User
		fields = ['username', 'password']
		extra_kwargs = {
			'password' : {'style':{'input_type':'password'}, 'write_only':True},
			'username' : {'help_text': None}
		}


class UserRegistrationSerializer(ModelSerializer):
	'''
	Serializer for User Registration 
		
	Fields:
	 	username: The name of the user.
		password: User password.
		password_confirmation: User password confirmation.
	'''
	password_confirmation = serializers.CharField(style={'input_type':'password'}, write_only=True)

	class Meta:
		model = User
		fields = ['pk', 'username', 'email', 'password', 'password_confirmation']
		extra_kwargs = {
			'password' : {'style':{'input_type':'password'}, 'write_only':True},
			'username' : {'help_text': None}
		}

	def validate(self, data):
		username = data.get('username').lower()
		if validate_username(username) == False:
			raise ValidationError(
				{"response": f"Username {username} is already in use."}
			)
		email = data.get('email').lower()
		if validate_email(email) == False:
			raise ValidationError(
				{"response": f"Email {email} is already in use."}
			)
		password = data.get('password')
		password_confirmation = data.get('password_confirmation')
		if password != password_confirmation:
			raise ValidationError(
				{"response": "Passwords must match"}
			)
		return data

	def create(self, validated_data):
		user = User.objects.create(
			username=validated_data['username'].lower(),
			email=validated_data['email'].lower(),
		)
		password=validated_data['password']
		user.set_password(password)
		user.save()
		return user


class UserChangePasswordSerializer(Serializer):
	'''
	Serializer for Change User Password

	Fields:
	 	old_password: Old user password.
		password: New user password.
		password_confirmation: New user password confirmation.
	'''
	old_password = serializers.CharField(required=True, style={'input_type':'password'})
	new_password = serializers.CharField(required=True, style={'input_type':'password'})
	confirm_new_password = serializers.CharField(required=True, style={'input_type':'password'})


class UserDetailsSerializer(ModelSerializer):
	'''
	Serializer for Get, Update, Delete User Account Atributes   

	Fields:
		username: New user name(for update).
		email: New user email(for update).
	'''

	class Meta:
		model = User
		fields = ['username', 'email']
		extra_kwargs = {
			'username' : {
						  'help_text': 'Enter a new username', 
						  'default':model.username,
						 },
			'email' : 	 {
					 	  'help_text': 'Enter a new email address', 
						   'default':model.email,
					  	 },
		}

	def update(self, instance, validated_data):
		context = {}

		old_username = instance.username.lower()
		new_username = validated_data.get('username').lower()
		if new_username != old_username and validate_username(new_username) == False:
			context["response"] = "Error"
			context["error_message"] = {"username": ["A user with that username already exists"]}
			raise ValidationError(context)
		else:
			instance.username = new_username

		old_email = instance.email.lower()
		new_email = validated_data.get('email').lower()
		if new_email != old_email and validate_email(new_email) == False:
			context["response"] = "Error"
			context["error_message"] = {"email": ["A user with that email already exist"]}
			raise ValidationError(context)
		else:
			instance.email = new_email
		
		instance.save()
		return instance


class UserSerializer(ModelSerializer):
	'''
	Serializer Dedicated for UserListApiView   

	Fields:
		id : The user id.
		username: The user acount name.
		email: The user email.
		token: The user current token or blank.
		date_joined: The date when user account was created.
		is_superuser: Does the user have administrator rights.
		is_staff: Does the user have staff rights.
		is_active: Does the user is active.
	'''

	token = serializers.SerializerMethodField('get_token')
	
	class Meta:
		model = User
		fields = ['id', 'username', 'email', 'token', 'date_joined',
				  'is_superuser', 'is_staff', 'is_active']

	def get_token(self, user):
		try:
			token = Token.objects.get(user=user).key
		except Token.DoesNotExist:
			token = ''
		return token