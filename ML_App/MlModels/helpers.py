import os
from . import models

def get_endpoint(instance):
	''' 
	Function returns base MlModel endpoint
	'''
	return f'{instance.name}_{instance.version}_{instance.created_at.date()}'


def create_endpoint(instance, new_endpoint=None, new_id=1):
	''' 
	Function create unique endpoint for MlModel
	'''
	if new_endpoint:
		endpoint = new_endpoint
	else:	
		endpoint = get_endpoint(instance)
	qs = models.MlModel.objects.filter(endpoint=endpoint).exclude(pk=instance.pk)
	exists = qs.exists()
	if exists:
		if new_endpoint:
			endpoint = f'{endpoint.rsplit("_", maxsplit=1)[0]}_{new_id}'
		else:
			endpoint = f'{endpoint}_{new_id}'
		new_id += 1
		return create_endpoint(instance, endpoint, new_id)
	return endpoint


def get_filepath(instance, *args):
	''' 
	Function returns MlModel file path
	'''
	return os.path.join('MlModels/algorithms', instance.endpoint)