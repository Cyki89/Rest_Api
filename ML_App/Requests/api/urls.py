from django.urls import path, include
from .views import (
	RequestCreateApiView,
	RequestDetailApiView,
	RequestListApiView
)
from ML_App.routers import DefaultRouterWithSimpleViews


router = DefaultRouterWithSimpleViews()
router.register(r'create', RequestCreateApiView, 'create')
router.register(r'list', RequestListApiView, 'list')

urlpatterns = [
    path('', include(router.urls)),
    path('<str:endpoint>/', RequestDetailApiView.as_view(), name='detail'),
]