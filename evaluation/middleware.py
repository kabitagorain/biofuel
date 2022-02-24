from .models import *
# from django.conf import settings
from django.utils import timezone
from . helper import claer_evaluator


class EvaMiddleware:  
    def __init__(self, get_response):
        """
        One-time configuration and initialisation.
        """
        self.get_response = get_response
        
    

    def __call__(self, request):
        """
        Code to be executed for each request before the view (and later
        middleware) are called.
        
        """
        
        
        
        
        '''
        delete evaluator without evaluationa fter each 1 hrs
        ''' 
        claer_evaluator(request)
        
        if 'evaluator' not in request.session:
            request.session['evaluator'] = ''    
        
            
            
            
          
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        '''
        do not delete below line. write anything before to call before view call
        '''    
        response = self.get_response(request) 
        
        # Code to be executed for each request/response after
        # the view is called.
        return response
    
    
        
        

        