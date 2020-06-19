from rest_framework.serializers import (
	ModelSerializer,
	SerializerMethodField,
)
from rest_framework import status
from MlModels import helpers
from MlModels.models import MlModel

class MlModelSerializer(ModelSerializer):
	'''
	MlModel serializer

	Fields:
		name: The name of the model.
		description: The short description of the model.
		version: The version of the model similar to software versioning.
		created_at: The date when algorithm was added.
		file: The reference to the physical algorithm file.
		endpoint: Represents algorithm endpoint.
		owner_name: The owner name.
	'''
	owner_name = SerializerMethodField('get_owner_name')
	created_at = SerializerMethodField('get_date')

	class Meta:
		model = MlModel
		fields = (
			'id',
			'name',
			'version',
			'description',
			'created_at',
			'file',
			'endpoint',
			'owner_name',
		)
		extra_kwargs = {
			'endpoint' : {'read_only':True},
			'file': {'write_only':True},
		}

	def get_owner_name(self, model):
		owner_name = model.owner.username
		return owner_name

	def get_date(self, model):
		date = model.created_at.date()
		return date


class MlModelListSerializer(ModelSerializer):
	'''
	MlModel serializer

	Fields:
		name: The name of the model.
		version: The version of the model similar to software versioning.
		endpoint: Represents algorithm endpoint.
		owner_name: The owner name.
		url: Hyperlink to algorithm.
	'''
	owner_name = SerializerMethodField('get_owner_name')

	class Meta:
		model = MlModel
		fields = (
			'name',
			'version',
			'endpoint',
			'owner_name',
			'url'
		)
		extra_kwargs = {
			'endpoint' : {'read_only':True},
			'url': {'view_name': 'MlModels-api:detail', 'lookup_field': 'endpoint'},
		}

	def get_owner_name(self, model):
		owner_name = model.owner.username
		return owner_name