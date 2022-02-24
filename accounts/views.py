from django.contrib import messages
from urllib.parse import urlparse
from django.http import HttpResponseRedirect
from .models import *
from .forms import UserCreationFormFront
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from gfvp import null_session
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string



def signup(request):
    
    if 'interested_in' not in request.session:
        request.session['interested_in'] = ''      
    
    
    slug_of_expart = UserType.objects.get(is_expert = True).slug
    
    
    if slug_of_expart == request.session['interested_in']:    
        request.session['hidden'] = ''
    else:
        request.session['hidden'] = 'hidden'
        
        
    if request.method == 'POST':
        current_site = get_current_site(request)
        form = UserCreationFormFront(request.POST)
        if form.is_valid():     
            new_user = form.save(commit=False)   
            new_user_type = form.cleaned_data['type']      
            '''if expert account will not auto activate'''  
            if new_user_type.is_expert:
                new_user.is_active = False
                new_user.save()
                
                subject = 'Please Wait for approval'                  
                
                # load a template like get_template() 
                # and calls its render() method immediately.
                message = render_to_string('emails/regi_mail_to_expert.html', {
                    'user': new_user,                    
                    'domain': current_site.domain,
                    
                })
                new_user.email_user(subject, message)
                
                messages.success(request, 'Your account has been created, please wait for approval!')
            else: 
                new_user.save()
                subject = 'Account has been created, you can login now!'                  
                
                # load a template like get_template() 
                # and calls its render() method immediately.
                message = render_to_string('emails/account_activated.html', {
                    'user': new_user,                    
                    'domain': current_site.domain,
                    
                })
                new_user.email_user(subject, message)
                
                messages.success(request, 'Your account has been created, you may login now!') 
            return HttpResponseRedirect(reverse_lazy('login'))
        else:
            messages.error(request, 'Invalid form submission.')
            messages.error(request, form.errors)
    else:
        
        try:
            type = UserType.objects.get(slug = request.session['interested_in'] )   
        except:
            type = None  
        
        initial_dict = {
            'type': type            
        }     
        
        form = UserCreationFormFront(initial = initial_dict)
        
    '''Ensure Selection of User Type based on session'''
    referer = urlparse(request.META.get('HTTP_REFERER')).path 
    try:       
        type_path = reverse('types', args=[str( request.session['interested_in'])] )
    except:
        type_path = None            
    if referer != type_path:  
        messages.warning(request, 'Select your business type!')      
        return HttpResponseRedirect(reverse('home:home'))
    
        
    context = {
        'form': form,
        'type': type
        
        
    }
    return render(request, 'registration/signup.html', context = context)

def userpage(request, username):
    context = {}
    return render(request, 'registration/userpage.html', context = context)



    
    
    
    
    
    
    

