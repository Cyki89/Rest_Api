from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from MlModels.models import MlModel
from .serializers import MlModelSerializer, MlModelListSerializer
from ML_App.permissions import IsAdminOrReadOnly


class MlModelCreateApiView(APIView):
	'''
	Rest Api View for New Algorithm Registration
	
	Fields:
	 	- name: The name of the model
        - description: The short description of the model
        - version: The version of the model similar to software versioning
        - file: Upload model file

	Requirements:
		- SuperUserAccount
	
	Available Actions:
		- Post: Register new model
	'''
	permission_classes = (IsAdminUser,)
	authentication_classes = (SessionAuthentication, TokenAuthentication,)
	serializer_class = MlModelSerializer

	def post(self, request):
		model = MlModel(owner=request.user)
		serializer = self.serializer_class(model, data=request.data)
		context = {}
		if serializer.is_valid():
			serializer.save()
			context['response'] = 'Successfully registered new model'
			context['data'] = serializer.data
			response_status = status.HTTP_201_CREATED
		else:
			context['response'] = 'Error'
			context['error_message'] = serializer.errors
			response_status = status.HTTP_400_BAD_REQUEST
		return Response(context, status=response_status)


class MlModelDetailApiView(APIView):
	'''
	Rest Api View for Algorithm Details
	
	Fields:
		- name: The name of the model
		- description: The short description of the model
		- version: The version of the model similar to software versioning
		- created_at: The date when algorithm was added
		- file: The reference to the physical algorithm file
		- endpoint: <course_title>_<algorithm.id>_<days>_<creation_date>
		- owner_name: The owner name

	Requirements:
		- Get: Session or Token Autentication
		- Put: Delete - Superuser status
	
	Available Actions:
		- Get: Retrive model data
		- Put: Update model data
		- Delete: Delete model from database
	'''
	serializer_class = MlModelSerializer
	permission_classes = (IsAuthenticated, IsAdminOrReadOnly)
	authentication_classes = (SessionAuthentication, TokenAuthentication,)

	def get(self, request, endpoint):
		model = get_object_or_404(MlModel, endpoint=endpoint)
		serializer = self.serializer_class(model)
		return Response(serializer.data)
		
	def put(self, request, endpoint):
		model = get_object_or_404(MlModel, endpoint=endpoint)
		context = {}
		data = request.data.dict()
		if not data['file']:
			data['file'] = model.file.file
		serializer = self.serializer_class(model, data=data, partial=True)
		if serializer.is_valid():
			serializer.save()
			context['response'] = 'Successfully update'
			context['data'] = serializer.data
			response_status = status.HTTP_200_OK
		else:
			context['response'] = 'Error'
			context['error_message'] = serializer.errors
			response_status = status.HTTP_400_BAD_REQUEST
		return Response(context, response_status)

	def delete(self, request, endpoint, format=None):
		model = get_object_or_404(MlModel, endpoint=endpoint)
		model.delete()
		response = 'Successfully deleted'
		response_status = status.HTTP_204_NO_CONTENT
		return Response({'response': response},status=response_status)


class MlModelListApiView(ListAPIView):
	'''
	Rest List Api View for Algorithms Query
	
	Fields:
		- name: The name of the model
		- version: The version of the model similar to software versioning
		- endpoint: <algorithm_name>_<version>_<addition_date>
		- owner_name: The owner name
		- url: Hyperlink to algorithm
	
	Requirements:
		- Autenticated User
	'''
	permission_classes = (IsAuthenticated,)
	authentication_classes = (SessionAuthentication, TokenAuthentication,)
	queryset = MlModel.objects.all().order_by('-created_at')
	serializer_class = MlModelListSerializer
	filter_backends = (SearchFilter,OrderingFilter)
	search_fields = ('name', 'owner__username', 'version')