from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import os
from .helpers import get_filepath, create_endpoint


class MlModel(models.Model):
	''' 
	Object represent ML Algorithm

	Atributes:
	 	name: The name of the algorithm.
        description: The short description of model.
        version: The version of the algorithm similar to software versioning.
        created_at: The date when algorithm was added.
        owner: The reference to the owner (User model).
        file: The reference to the physical algorithm file.
        endpoint: Represents algorithm endpoint.
	'''
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=128)
	version = models.CharField(max_length=16)
	created_at = models.DateTimeField(default=timezone.now)
	description = models.TextField(max_length=1000, blank=True)
	endpoint = models.SlugField(max_length=256, unique=True, blank=True)
	file = models.FileField(upload_to=get_filepath, max_length=256)

	class Meta():
		verbose_name = "MlModel"
		verbose_name_plural = "MlModels"

	def __str__(self):
		return f'{os.path.basename(self.file.name)}'

	def save(self, *args, **kwargs):
		self.endpoint = create_endpoint(self)
		super(MlModel, self).save(*args, **kwargs)