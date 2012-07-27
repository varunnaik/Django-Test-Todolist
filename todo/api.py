from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from todo.models import Item
from django.contrib.auth.models import User
from tastypie import fields
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization, Authorization

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username']
        allowed_methods = ['get']
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
    
    def get_object_list(self, request):
        """Ensure users can see only their own username in the user list"""
        return super(UserResource, self).get_object_list(request).filter(username=request.user.username)

        
class TodoResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    class Meta:
        queryset = Item.objects.all()
        resource_name = 'todo'
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods=['get', 'put', 'delete']
        authentication = BasicAuthentication()
        authorization = Authorization()
    
    def get_object_list(self, request):
        """Ensure users can see only their own todo items"""
        return super(TodoResource, self).get_object_list(request).filter(user=request.user)
        
    def obj_create(self, bundle, request=None, **kwargs):    
        return super(TodoResource, self).obj_create(bundle, request, user=request.user)

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user=request.user)
