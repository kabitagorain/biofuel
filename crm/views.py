import csv
from django.db import IntegrityError
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from gfvp import null_session
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import *
import random
from django.contrib.sites.models import Site
from django.contrib import messages
from .forms import UploadLead
from django.core.files.storage import default_storage
import os


#helper function
def random_digits():
    return "%0.12d" % random.randint(0, 999999999999)

@staff_member_required
def leads(request):
    #default behavior to avoid error
    null_session(request)
    #Post method event
    if request.method == "POST": 
        print(request.POST) 
        
        
        if 'delete_lead' in request.POST:
            #If no data selected return
            if not request.POST.getlist('lead'):
                messages.warning(request, "Please select lead")
                return HttpResponseRedirect(reverse('crm:leads')) 
            #get selected data 
            lead_ids = request.POST.getlist('lead')
            #delete selected lead   
            delete_count = 0         
            for li in lead_ids:
                Lead.objects.get(id = li).delete()
                delete_count += 1
            messages.success(request, f"{ delete_count } lead deleted successfully.")
                   
        
        
        if 'add_lead' in request.POST:       
             
            #If no data selected return
            if not request.POST.getlist('lead'):
                messages.warning(request, "Please select lead")
                return HttpResponseRedirect(reverse('crm:leads'))   
            
            #Allowed 50 email per action to reduce RAM load
            if len(request.POST.getlist('lead')) > 50:
                messages.warning(request, "Please select less then 50! " + "There was " + str(len(request.POST.getlist('lead'))) + " selected!" )
                return HttpResponseRedirect(reverse('crm:leads'))       
            
            #get selected data 
            lead_ids = request.POST.getlist('lead')  
            
            # If no qualified lead found system will redirect.
            try:      
                result_lead = Lead.objects.filter(pk__in = lead_ids, subscribed = True) 
            except:
                messages.warning(request, "No Subscribed lead found")
                return HttpResponseRedirect(reverse('crm:leads'))  
            
            #Process Mail        
            from django.template.loader import render_to_string
            from django.core.mail import send_mass_mail       
            current_site = Site.objects.get_current()
            subject = current_site.domain + ' miss you!'    
            mail_to_lead = []
            sent_count = 1
            for rl in result_lead:            
                
                #To protect to be unsubscribe lead by robotic action
                confirm_code = random_digits()
                lead = Lead.objects.get(email_address = rl.email_address)
                lead.confirm_code = confirm_code
                lead.save() 
                
                sent_count += 1
                
                
                #process mail template
                message = render_to_string('emails/crm_initial_mail.html', {
                    'confirm_code': confirm_code,
                    'lead' : rl,                                                               
                    'domain': current_site.domain,            
                    })  
                mail_to_lead.append((subject, message, 'from@example.com', [rl.email_address]))
                
            #send bulk mail using only one conenction
            send_mass_mail((mail_to_lead), fail_silently=False)
            messages.success(request, f"{sent_count} Mail sent successfully ")
            
        if 'lead_upload' in request.FILES:
            
            upload_csv_form = UploadLead(request.POST, request.FILES)
            if upload_csv_form.is_valid():
                
                lead_upload = upload_csv_form.cleaned_data['lead_upload']   
                
                
                
                if not lead_upload.name.endswith('.csv'):
                    messages.error(request, 'File is not CSV type! Pleas Save your excel file in .csv format')
                    return HttpResponseRedirect(reverse('crm:leads'))  
                
                if lead_upload.multiple_chunks():
                    messages.error(request, 'Uploaded file is too big (%.2f MB)' %(lead_upload.size(1000*1000),))
                    return HttpResponseRedirect(reverse('crm:leads'))  
                
                
                data = csv.DictReader(chunk.decode() for chunk in lead_upload)
                entry_count = 0
                error_count = 0
                
                for d in data:                    
                    try:
                        new_lead = Lead(lead = str(d['lead']), email_address = str(d['email_address']), phone = str(d['phone']), address_1 = str(d['address_1']), address_2 = str(d['address_2']), country = str(d['country_code']), city = str(d['city']))
                        new_lead.save()
                        entry_count += 1
                    except Exception as e:
                        error_count += 1
                messages.success(request, f'{entry_count} lead has beed added! \n')
                messages.error(request, f"\n There was {error_count} error! Please check file format, record's title and duplicate email before each upload! \n")
                        
                    
                    
                # file = open(default_storage.path('tmp/'+lead_upload.name))

                # csvreader = csv.DictReader(file)
                
                # for r in csvreader:
                #     print(r)
                #     if r != 0:
                #         del(r)
                    
                    
                    
                
                
                
                
                # with open(default_storage.path('tmp/'+lead_upload.name), 'wb+') as destination:
                    
                #     for chunk in lead_upload.chunks():
                        
                #         destination.write(chunk)
                #     data = csv.reader(lead_upload, dialect='excel')
                #     print(data)
                #     for d in data:
                #         print(d)
                    # next(data)
                
                # with open(lead_upload, 'wb+') as destination:
                    
                #     for chunk in lead_upload.chunks():
                #         destination.write(chunk)
                #     data = csv.reader(default_storage.path('tmp/'+f.name))
                #     print(data)
            
            
    upload_csv_form = UploadLead()
    
        
    #List of Lead
    leads = Lead.objects.all()
    
    
    context = {        
        'leads': leads,
        'upload_csv_form': upload_csv_form
    }
    return render(request, 'crm/leads.html', context = context)

def unsubscrib(request, **kwargs):  
    
    try:  
        lead = Lead.objects.get(email_address = kwargs['email'], confirm_code = kwargs['code'])
        lead.subscribed = False
        lead.save()    
    except:
        messages.warning(request, "No email found!")
        return HttpResponseRedirect(reverse('home:home'))        
        
        
    return render(request, 'crm/unsubscribed.html', {'lead': lead, 'action': 'unsubscribed'})

def subscrib(request, **kwargs):    
    try:
        lead = Lead.objects.get(email_address = kwargs['email'])
        lead.subscribed = True
        lead.save()    
    except:
        messages.warning(request, "No email found!")
        return HttpResponseRedirect(reverse('home:home'))      
        
    return render(request, 'crm/subscribed.html', {'lead': lead, 'action': 'subscribed'})

def upload_lead(request):
    if request.method =='POST':
        form = UploadLead(request.FILES)   
             
    