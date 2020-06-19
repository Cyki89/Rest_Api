from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
	'''
	Custom permission class
	Check if the current user is owner of the object
	if not then user have only permission to read data(GET)
	'''
	def has_object_permission(self, request, view, obj):
		return obj.owner == request.user



class IsAdminOrReadOnly(BasePermission):
	'''
	Custom permission class
	Check if the current user is have admin right
	if not then user have only permission to read data(GET)
	'''
	def has_object_permission(self, request, view, obj):
		return request.user.is_staff