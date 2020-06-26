from django.contrib.auth.models import User
from django.db.models import signals
from django.utils import timezone

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from unittest.mock import patch

from .models import MlModel

import os
import factory


class CreateModelTestCase(APITestCase):

	def setUp(self):
		self.user = User.objects.create_user(username="testuser",
											 email="testuser@email.com",
		                         			 password="some_strong_psw")

	def test_create_model(self):
		self.user.is_staff = True
		self.client.force_authenticate(user=self.user)

		curr_date = timezone.now().date()
		model_path = "./MlModels/algorithms/SVR_V1_2020-06-19"

		with open(model_path, "rb") as file:
			data = {
				"name" : "SVR",
				"version" : "V1",
				"description": "First Version",
				"file" : file,
			}
			response = self.client.post("/api/models/create/", data)

		expected_response = {
		    "response": "Successfully registered new model",
		    "data": {
		        "id": 1,
		        "name": "SVR",
		        "version": "V1",
		        "description": "First Version",
		        "created_at": curr_date,
		        "endpoint": f"SVR_V1_{curr_date}",
		        "owner_name": self.user.username
		    }
		}

		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(MlModel.objects.count(), 1)
		
		new_model_path = os.path.join('./MlModels/algorithms', response.data['data']['endpoint'])
		if os.path.isfile(new_model_path):
		    os.remove(new_model_path)

	def test_no_permissions(self):
		self.client.force_authenticate(user=self.user)

		data = {}
		response = self.client.post("/api/models/create/", data)

		expected_response = { "detail": "You do not have permission to perform this action." }

		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
		self.assertEqual(MlModel.objects.count(), 0)


class ModelsListTestCase(APITestCase):

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

	def test_models_list(self):
		response = self.client.get("/api/models/list/")

		new_model = MlModel.objects.first()
		expected_response = {
		    "count": MlModel.objects.count(),
		    "next": None,
		    "previous": None,
		    "results": [
		        {
		            "name": new_model.name,
		            "version": new_model.version,
		            "endpoint": new_model.endpoint,
		            "owner_name": new_model.owner.username,
		            "url": f"http://testserver/api/models/{new_model.endpoint}/"
		        },
		    ]
		}

		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		new_model_path = os.path.join('./MlModels/algorithms', new_model.endpoint)
		if os.path.isfile(new_model_path):
			os.remove(new_model_path)


class ModelDetailsTestCase(APITestCase):

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

		self.new_model = MlModel.objects.first()
		self.new_model_path = os.path.join('./MlModels/algorithms', self.new_model.endpoint)

		self.curr_date = timezone.now().date()

	def test_get(self):
		response = self.client.get(f"/api/models/{self.new_model.endpoint}/")

		expected_response = {
		    "id": self.new_model.pk,
		    "name": self.new_model.name,
		    "version": self.new_model.version,
		    "description": self.new_model.description,
		    "created_at": self.curr_date,
		    "endpoint": self.new_model.endpoint,
		    "owner_name": self.new_model.owner.username
		}

		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	# to disable auto_delete_file_on_delete
	@factory.django.mute_signals(signals.post_delete)
	def test_delete(self):
		response = self.client.delete(f"/api/models/{self.new_model.endpoint}/")

		expected_response = {
    		"response": "Successfully deleted"
		}		

		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(MlModel.objects.count(), 0)
	
	# to disable auto_change_file_on_update method
	@factory.django.mute_signals(signals.pre_save)
	def test_put(self):
		data = {
				"version": "V2",
				"description": "Seccond Version",
				"file": ""
		}
		response = self.client.put(f"/api/models/{self.new_model.endpoint}/", data)

		expected_response = {
			"response": "Successfully update",
			"data": {
			    "id": self.new_model.pk,
			    "name": self.new_model.name,
			    "version": data['version'],
			    "description": data['description'],
			    "created_at": self.curr_date,
			    "endpoint": f"{self.new_model.name}_{data['version']}_{self.curr_date}",
			    "owner_name": self.new_model.owner.username
			}
		}

		self.assertEqual(response.data, expected_response)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		# delete new create file
		updated_model_path = os.path.join('./MlModels/algorithms', expected_response['data']['endpoint'])
		if os.path.isfile(updated_model_path):
			os.remove(updated_model_path)