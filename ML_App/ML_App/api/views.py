from rest_framework.response import Response
from rest_framework.views import APIView


class MainAPIView(APIView):
    '''
    Main Rest Api View for Browsable API 
    '''
    def get(self, request):
        data = {
            'users_router': 'http://127.0.0.1:8000/api/users/',
            'models_router' : 'http://127.0.0.1:8000/api/models/',
            'requests_router' : 'http://127.0.0.1:8000/api/requests/',
        }
        return Response(data)