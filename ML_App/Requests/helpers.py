import os
from Requests import models

def get_endpoint(instance):
	''' 
	Function returns base Request endpoint
	'''
	course_title = instance.course_title.lower().replace(' ', '-')
	return f'{course_title}_{instance.algorithm.id}_{instance.days}_{instance.created_at.date()}'


def create_endpoint(instance, new_endpoint=None, new_id=1):
	''' 
	Function create unique endpoint for Request
	'''
	if new_endpoint:
		endpoint = new_endpoint
	else:	
		endpoint = get_endpoint(instance)
	qs = models.Request.objects.filter(endpoint=endpoint).exclude(pk=instance.pk)
	exists = qs.exists()
	if exists:
		if new_endpoint:
			endpoint = f'{endpoint.rsplit("_", maxsplit=1)[0]}_{new_id}'
		else:
			endpoint = f'{endpoint}_{new_id}'
		new_id += 1
		return create_endpoint(instance, endpoint, new_id)
	return endpoint