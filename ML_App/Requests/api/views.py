from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from .serializers import (
	RequestCreateUpdateSerializer,
	RequestDetailSerializer, 
	RequestListSerializer
)
from Requests.models import Request
from ML_App.permissions import IsOwnerOrReadOnly


class RequestBaseApiView(APIView):
	"""
	Base Class for Request Create/Update Api Views
	"""
	serializer_class = RequestCreateUpdateSerializer
	permission_classes = (IsAuthenticated,)
	authentication_classes = (SessionAuthentication, TokenAuthentication,)

	def response(self, request, serializer, succes_status):
		if serializer.is_valid():
			request_data = serializer.save(owner=request.user)

			input_data = {}
			input_data['course_title'] = request_data.course_title
			input_data['price'] = request_data.price
			input_data['content_duration'] = request_data.content_duration
			input_data['num_lectures'] = request_data.num_lectures
			input_data['days'] = request_data.days 
			input_data['level'] = request_data.level
			
			response_data = {}
			response_data['response'] = 'Successfully Create/Update Request'
			response_data['input_data'] = input_data
			response_data['algorithm'] = request_data.algorithm.__str__()
			response_data['prediction'] = request_data.prediction
			response_data['created_at'] = request_data.created_at.date()
			response_data['endpoint'] = request_data.endpoint
			response_data['owner'] = request_data.owner.username

			return Response(data=response_data, status=succes_status)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		

class RequestCreateApiView(RequestBaseApiView):
	"""
	Rest Api View for Create Prediction Request

	Fields:
	 	- course_title: The name of the courses
        - price: The price in $
        - content_duration: The course time duration in hours
        - num_lectures: The number of course lectures
        - level: The experience level of the course
        - days: Number of days to predict the number of subscribers
        - algorithm: Related algorithm

    Requirements:
		- Active user
		- Session or Token Autentication
	
	Available Actions:
		- Post: Create new prediction request
	"""
	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		return self.response(request, serializer, succes_status=status.HTTP_201_CREATED)


class RequestDetailApiView(RequestBaseApiView):
	"""
	Rest Api View for Prediction Request Detail
	
	Fields:
	 	- course_title: The name of the courses
        - price: The price in $
        - content_duration: The course time duration in hours
        - num_lectures: The number of course lectures
        - level: The experience level of the course
        - days: Number of days to predict the number of subscribers
        - prediction: Predicted number of subscribers
        - created_at: Date of request
        - endpoint: <course_title>_<algorithm.id>_<days>_<creation_date>
        - algorithm: Related algorithm details
        - owner_name: User who made request

    Requirements:
    	- Active user
    	- Session or Token Autentication 
		- Put: Delete - Active User is owner of the request
	
	Available Actions:
		- Get: Retrive prediction request data
		- Put: Update prediction request(only input data) data
		- Delete: Delete prediction request from database
	"""
	permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

	def get(self, request, endpoint):
		request_model = get_object_or_404(Request, endpoint=endpoint)
		serializer = RequestDetailSerializer(request_model)
		return Response(serializer.data)

	def put(self, request, endpoint):
		request_model = get_object_or_404(Request, endpoint=endpoint)
		serializer = self.serializer_class(request_model, data=request.data, partial=True)
		return self.response(request, serializer, succes_status=status.HTTP_200_OK)

	def delete(self, request, endpoint):
		request_model = get_object_or_404(Request, endpoint=endpoint)
		request_model.delete()
		response = 'Successfully deleted'
		response_status = status.HTTP_204_NO_CONTENT
		return Response({'response': response}, status=response_status)


class RequestListApiView(ListAPIView):
	"""
	Rest List Api View for Prediction Request
	
	Fields:
	 	- course_title: The name of the courses
        - prediction: Predicted number of subscribers
        - endpoint: <course_title>_<algorithm.id>_<days>_<creation_date>
        - algorithm: Related algorithm endpoint
        - owner_name: User who made request
        - url: Hyperlink to prediction request detail
	"""
	permission_classes = (IsAuthenticated,)
	authentication_classes = (SessionAuthentication, TokenAuthentication,)
	queryset = Request.objects.all().order_by('-created_at')
	filter_backends = (SearchFilter,OrderingFilter)
	search_fields = ('course_title', 'owner__username', 'level', 'algorithm__endpoint')
	serializer_class = RequestListSerializer