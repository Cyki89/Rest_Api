from rest_framework import serializers
from rest_framework.serializers import(
	ValidationError, 
	ModelSerializer,
	SerializerMethodField,
)
from Requests.models import Request
from MlModels.api.serializers import MlModelSerializer
from Prediction_Pipeline.prediction_pipeline import make_prediction
from ML_App.settings import LEVEL_CHOICES


class RequestCreateUpdateSerializer(ModelSerializer):
	''' 
	Request Serializer for Create/Update Api View
	
	Fields:
	 	course_title: The name of the courses.
        price: The price in $.
        content_duration: The course time duration in hours.
        num_lectures: The number of course lectures.
        level: The experience level of the course.
        days: Number of days to predict the number of subscribers.
        algorithm: Related algorithm.
	'''

	class Meta:
		model = Request
		fields = (
			'course_title',
			'price',
			'content_duration',
			'num_lectures',
			'days',
			'level',
			'algorithm',
		)

	def validate(self, input_data):
		MIN_PRICE, MAX_PRICE = 20, 200
		MIN_CONTENT_DURATION = 1
		MIN_NUM_LECTURES = 1

		if input_data['price'] < MIN_PRICE or input_data['price'] > MAX_PRICE:
			raise ValidationError(
				{"response": f"Course Price has to be in range {MIN_PRICE}-{MAX_PRICE}$ (Udemy Limits)"}
			)

		if input_data['content_duration'] < MIN_CONTENT_DURATION:
			raise ValidationError(
				{"response": f"Course should be at least {MIN_CONTENT_DURATION} hour long"}
			)

		if input_data['num_lectures'] < MIN_CONTENT_DURATION:
			raise ValidationError(
				{"response": f"Course should have at least {MIN_NUM_LECTURES} lecture"}
			)

		input_data['course_title'] = input_data['course_title'].lower()

		return input_data


class RequestDetailSerializer(ModelSerializer):
	''' 
	Request Serializer for Retrive Api View
	
	Fields:
	 	course_title: The name of the courses.
        price: The price in $.
        content_duration: The course time duration in hours.
        num_lectures: The number of course lectures.
        level: The experience level of the course.
        days: Number of days to predict the number of subscribers.
        prediction: Predicted number of subscribers.
        created_at: Date of request.
        endpoint: Represents prediction request object endpoint.
        algorithm: Related algorithm details.
        owner_name: User who made request.
	'''
	owner_name = SerializerMethodField('get_owner_name')
	created_at = SerializerMethodField('get_date')
	prediction = SerializerMethodField('get_prediction')
	algorithm = MlModelSerializer()

	class Meta:
		model = Request
		fields = (
			'course_title',
			'price',
			'content_duration',
			'num_lectures',
			'days',
			'level',
			'prediction',
			'created_at',
			'endpoint',
			'algorithm',
			'owner_name',
		)
		extra_kwargs = {
			'algorithm': {'read_only': True},
		}


	def get_owner_name(self, model):
		owner_name = model.owner.username
		return owner_name

	def get_date(self, model):
		date = model.created_at.date()
		return date

	def get_prediction(self, model):
		prediction = model.prediction
		return prediction


class RequestListSerializer(ModelSerializer):
	''' 
	Request Serializer for List/Retrive Api View
	
	Fields:
	 	course_title: The name of the courses.
        prediction: Predicted number of subscribers.
        endpoint: Represents Request object endpoint.
        algorithm: Related algorithm endpoint.
        owner_name: User who made request.
        url: Hyperlink to prediction request details.
	'''
	owner_name = SerializerMethodField('get_owner_name')
	prediction = SerializerMethodField('get_prediction')
	algorithm = SerializerMethodField('get_algorithm')


	class Meta:
		model = Request
		fields = (
			'course_title',
			'prediction',
			'endpoint',
			'algorithm',
			'owner_name',
			'url'
		)
		extra_kwargs = {
			'url': {'view_name': 'Requests-api:detail', 'lookup_field': 'endpoint'},
		}

	def get_owner_name(self, model):
		owner_name = model.owner.username
		return owner_name

	def get_algorithm(self, model):
		algorithm = model.algorithm.__str__()
		return algorithm

	def get_prediction(self, model):
		prediction = model.prediction
		return prediction