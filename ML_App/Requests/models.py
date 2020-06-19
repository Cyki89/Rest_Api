from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from ML_App.settings import LEVEL_CHOICES
from MlModels.models import MlModel
from .helpers import create_endpoint
from Prediction_Pipeline.prediction_pipeline import make_prediction


class Request(models.Model):
	''' 
	Object represent single prediction request 

	Atributes:
	 	course_title: The name of the courses.
        price: The price in $.
        content_duration: The course time duration in hours.
        num_lectures: The number of course lectures.
        level: The experience level of the course.
        days: Number of days to predict the number of subscribers.
        prediction: Predicted number of subscribers.
        created_at: Date of request.
        algorithm: Related algorithm.
        owner: User who made request.
        endpoint: Represents Request object endpoint.
	'''
	# input data fields
	course_title = models.CharField(max_length=128, blank=True)
	price = models.FloatField(default=100)
	content_duration = models.FloatField(default=20)
	num_lectures = models.IntegerField(default=20)
	level = models.CharField(
		max_length=32,
	 	default='All Levels', 
	 	choices=LEVEL_CHOICES
	 )
	days = models.IntegerField(default=365)

	# request data fields
	prediction = models.FloatField(blank=True)
	created_at = models.DateTimeField(default=timezone.now)

	# relational fields
	endpoint = models.SlugField(max_length=256, unique=True, blank=True)
	algorithm = models.ForeignKey(MlModel, on_delete=models.CASCADE)
	owner = models.ForeignKey(User, on_delete=models.CASCADE)

	class Meta():
		verbose_name = "Request"
		verbose_name_plural = "Requests"

	def __str__(self):
		return f'{create_endpoint(self)}'

	def save(self, *args, **kwargs):
		self.prediction = round(make_prediction(self)[0])
		self.endpoint = self.__str__()
		super(Request, self).save(*args, **kwargs)
