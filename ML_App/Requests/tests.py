from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from MlModels.models import MlModel
from .models import Request

import warnings
warnings.filterwarnings("ignore")

import os


class CreateRequestTestCase(APITestCase):

	def setUp(self):
		self.user = User.objects.create_user(username="testuser",
											 email="testuser@email.com",
		                         			 password="some_strong_psw")

		self.model_path = "./MlModels/algorithms/SVR_V1_2020-06-19"
		self.model = MlModel.objects.create(owner=self.user,
											name='SVR',
											version='V1',
											description='First Version',
											file=self.model_path)
		self.client.force_authenticate(user=self.user)

	def test_create_request(self):

		data = {
			"course_title": "Django Web Course",
			"price": 100,
			"content_duration": 40,
			"num_lectures": 40,
			"days": 365,
			"level": "All Levels",
			"algorithm": self.model.pk,
		}
		response = self.client.post("/api/requests/create/", data)

		curr_date = timezone.now().date()
		expected_response = {
			"response": "Successfully Create/Update Request",
			"input_data": {
			    "course_title": data['course_title'].lower(),
			    "price": data['price'],
			    "content_duration": data['content_duration'],
			    "num_lectures": data['num_lectures'],
			    "days": data['days'],
			    "level": data['level']
			},
			"algorithm": os.path.basename(self.model_path),
			"prediction": response.data['prediction'],
			"created_at": curr_date,
			"endpoint": response.data['endpoint'],
			"owner": self.user.username
			}

		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Request.objects.count(), 1)

	def test_no_permissions(self):
		self.client.force_authenticate(user=None)

		data = {}
		response = self.client.post("/api/requests/create/", data)

		expected_response = { "detail": "Authentication credentials were not provided." }

		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
		self.assertEqual(Request.objects.count(), 0)

	def test_wrong_price(self):

		data = {
			"course_title": "Django Web Course",
			"price": 300,
			"content_duration": 40,
			"num_lectures": 40,
			"days": 365,
			"level": "All Levels",
			"algorithm": self.model.pk,
		}
		response = self.client.post("/api/requests/create/", data)

		expected_response =	{
		    "response": [
		        "course price has to be in range 20-200$ (Udemy Limits)"
		    ]
		}

		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Request.objects.count(), 0)

	def test_wrong_content_duration(self):

		data = {
			"course_title": "Django Web Course",
			"price": 100,
			"content_duration": 0,
			"num_lectures": 40,
			"days": 365,
			"level": "All Levels",
			"algorithm": self.model.pk,
		}
		response = self.client.post("/api/requests/create/", data)

		expected_response =	{
		    "response": [
		        "course should be at least 1 hour long"
		    ]
		}

		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Request.objects.count(), 0)

	def test_wrong_num_lectures(self):

		data = {
			"course_title": "Django Web Course",
			"price": 100,
			"content_duration": 40,
			"num_lectures": 0,
			"days": 365,
			"level": "All Levels",
			"algorithm": self.model.pk,
		}
		response = self.client.post("/api/requests/create/", data)

		expected_response =	{
		    "response": [
		        "course should have at least 1 lecture"
		    ]
		}

		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Request.objects.count(), 0)

	def test_wrong_num_days(self):

		data = {
			"course_title": "Django Web Course",
			"price": 100,
			"content_duration": 40,
			"num_lectures": 40,
			"days": 0,
			"level": "All Levels",
			"algorithm": self.model.pk,
		}
		response = self.client.post("/api/requests/create/", data)

		expected_response =	{
		    "response": [
		        "number of days can't be smaller than 1"
		    ]
		}

		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Request.objects.count(), 0)


class RequestListTestCase(APITestCase):

	def setUp(self):
		self.user = User.objects.create_user(username="testuser",
											 email="testuser@email.com",
		                         			 password="some_strong_psw")

		self.model_path = "./MlModels/algorithms/SVR_V1_2020-06-19"
		self.model = MlModel.objects.create(owner=self.user,
											name='SVR',
											version='V1',
											description='First Version',
											file=self.model_path)
		
		self.request = Request.objects.create(course_title="Django Web Course",
											  price=100,
											  content_duration=40,
											  num_lectures=40,
											  days=365,
											  level="All Levels",
											  owner=self.user,
								              algorithm=self.model)

		self.client.force_authenticate(user=self.user)

	def test_models_list(self):
		response = self.client.get("/api/requests/list/")

		expected_response = {
		    "count": Request.objects.count(),
		    "next": None,
		    "previous": None,
		    "results": [
				{
			        "course_title": self.request.course_title,
			        "prediction": self.request.prediction,
			        "endpoint": self.request.endpoint,
			        "algorithm": os.path.basename(self.model_path),
			        "owner_name": self.user.username,
			        "url": f"http://testserver/api/requests/{self.request.endpoint}/"
			    }
		    ]
		}

		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(Request.objects.count(), 1)


class RequestDetailsTestCase(APITestCase):

	def setUp(self):
		self.user = User.objects.create_user(username="testuser",
											 email="testuser@email.com",
		                         			 password="some_strong_psw")
		self.client.force_authenticate(user=self.user)

		self.model_path = "./MlModels/algorithms/SVR_V1_2020-06-19"
		self.model = MlModel.objects.create(owner=self.user,
											name='SVR',
											version='V1',
											description='First Version',
											file=self.model_path)
		
		self.request = Request.objects.create(course_title="Django Web Course",
											  price=100,
											  content_duration=40,
											  num_lectures=40,
											  days=365,
											  level="All Levels",
											  owner=self.user,
								              algorithm=self.model)

		self.curr_date = timezone.now().date()
		
	def test_get(self):
		response = self.client.get(f"/api/requests/{self.request.endpoint}/")

		expected_response = {
			"course_title": self.request.course_title,
			"price": self.request.price,
			"content_duration": self.request.content_duration,
			"num_lectures": self.request.num_lectures,
			"days": self.request.days,
			"level": self.request.level,
			"prediction": self.request.prediction,
			"created_at": self.curr_date,
			"endpoint": self.request.endpoint,
			"algorithm": {
			    "id": self.request.algorithm.pk,
			    "name": self.request.algorithm.name,
			    "version": self.request.algorithm.version,
			    "description": self.request.algorithm.description,
			    "created_at": self.request.algorithm.created_at.date(),
			    "endpoint": self.request.algorithm.endpoint,
			    "owner_name": self.request.algorithm.owner.username
			    },
			"owner_name": self.request.owner.username
		}

		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_delete(self):
		response = self.client.delete(f"/api/requests/{self.request.endpoint}/")

		expected_response = {
    		"response": "Successfully deleted"
		}		

		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(Request.objects.count(), 0)

	
	def test_put(self):
		data = {
		        "course_title": "django web course",
		        "price": 200.0,
		        "content_duration": 80.0,
		        "num_lectures": 80,
		        "days": 730,
		        "level": "All Levels"
		}
		response = self.client.put(f"/api/requests/{self.request.endpoint}/", data)

		expected_response = {
		    "response": "Successfully Create/Update Request",
		    "input_data": {
		        "course_title": data['course_title'],
		        "price": data['price'],
		        "content_duration": data['content_duration'],
		        "num_lectures": data['num_lectures'],
		        "days": data['days'],
		        "level": data['level']
		    },
		    "algorithm": os.path.basename(self.model_path),
		    "prediction": response.data['prediction'],
		    "created_at": self.curr_date,
		    "endpoint": response.data['endpoint'],
		    "owner": self.user.username
		}

		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
