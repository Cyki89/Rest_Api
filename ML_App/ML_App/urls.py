from django.contrib import admin 
from django.urls import path, include
from .api.views import MainAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include(('Users.api.urls', 'Users-api'), namespace='Users-api')),
    path('api/models/', include(('MlModels.api.urls', 'MlModels-api'), namespace='MlModels-api')),
    path('api/requests/', include(('Requests.api.urls', 'Requests-api'), namespace='Requests-api')),
    path('', MainAPIView.as_view(), name='Main-api'),
]
