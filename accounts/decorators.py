from django.core.exceptions import PermissionDenied
from django.http.response import Http404, HttpResponseRedirect, HttpResponse
from django.urls.base import reverse
from django.contrib import messages


def expert_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_expert or request.user.is_staff or request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:            
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__                
    return wrap

def producer_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_producer or request.user.is_staff or request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:            
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__                
    return wrap

def consumer_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_consumer or request.user.is_staff or request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:            
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__                
    return wrap

