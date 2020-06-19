from django.urls import path, include
from .views import (
	UserRegistrationApiView,
	UserLoginApiView, 
	UserLogoutApiView,
	ObtainAuthTokenView,
	UserChangePasswordApiView,
	UserDetailsApiView,
	UserListApiView,
)
from ML_App.routers import DefaultRouterWithSimpleViews


router = DefaultRouterWithSimpleViews()
router.register(r'register', UserRegistrationApiView, 'register')
router.register(r'login', UserLoginApiView, 'login')
router.register(r'logout', UserLogoutApiView, 'logout')
router.register(r'token-auth', ObtainAuthTokenView, 'token-auth')
router.register(r'change-password', UserChangePasswordApiView, 'change-password')
router.register(r'user-details', UserDetailsApiView, 'user-details')
router.register(r'user-list', UserListApiView, 'user-list')

urlpatterns = router.urls