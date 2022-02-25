from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from evaluation.models import *
from accounts.models import *
from django.db.models import Count, Min




def check_type(request, slug):   
    try:
        curnt_user_type_slug = request.user.type.slug
    except Exception as e:
        
        curnt_user_type_slug = None 
     
    if curnt_user_type_slug == slug or request.user.is_staff or request.user.is_superuser:
        pass
    else:
        raise PermissionDenied
    

    