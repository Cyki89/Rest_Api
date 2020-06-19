from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


def validate_email(email):
	'''
	Helper Function to check if email exists in database
	'''
	if email in map(lambda x: x.email.lower(), User.objects.all()):
		return False
	return True


def validate_username(username):
	'''
	Helper Function to check if username exists in database
	'''
	if username in map(lambda x: x.username.lower(), User.objects.all()):
		return False
	return True


def get_or_create_token(user):
	'''
	Helper Function to return an auth token or create a new on and return it
	'''
	try:
		token = Token.objects.get(user=user)
	except Token.DoesNotExist:
		token = Token.objects.create(user=user)
	return token