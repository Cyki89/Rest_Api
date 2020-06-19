from django.urls import path, include
from .views import (
	MlModelCreateApiView,
	MlModelDetailApiView,
	MlModelListApiView
)
from ML_App.routers import DefaultRouterWithSimpleViews


router = DefaultRouterWithSimpleViews()
router.register(r'create', MlModelCreateApiView, 'create')
router.register(r'list', MlModelListApiView, 'list')

urlpatterns = [
    path('', include(router.urls) ),
    path('<str:endpoint>/', MlModelDetailApiView.as_view(), name='detail'),  
]
