from email.policy import default
from django.forms import model_to_dict
from evaluation.models import DifinedLabel
# import evaluation.models.DifinedLabel

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class UserType(models.Model):
    name = models.CharField(max_length=252)    
    slug = models.SlugField(unique=True, null=False, blank=False)
    # svg_path = models.TextField()
    icon = models.ImageField(upload_to = 'usertype/')
    created = models.DateTimeField(auto_now_add=True)
    is_producer = models.BooleanField(default=False)
    is_expert = models.BooleanField(default=False)
    is_consumer = models.BooleanField(default=False)    
    sort_order = models.IntegerField(default=1)
    active = models.BooleanField(default=False)
   
    
    def get_absolute_url(self):        
        return reverse('types', args=[str(self.slug)])

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        permissions = (("can_access_usertype", "Can access usertype"),)


class User(AbstractUser):    
    type = models.ForeignKey(UserType, on_delete=models.CASCADE, null=True, blank=True) 
    
    
    email = models.EmailField('email address', unique=True)
    phone = models.CharField(max_length=252, null=True, blank=True)
    orgonization = models.CharField(max_length=252, null=True, blank=True)
    experts_in = models.ForeignKey(DifinedLabel, on_delete=models.SET_NULL, null=True, blank=True, related_name = 'user_label', limit_choices_to={'common_status': False} )  
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    

    def __str__(self):
        return self.email
    
    def send_active_mail(self, request):
        from django.template.loader import render_to_string
        from django.contrib.sites.shortcuts import get_current_site
        current_site = get_current_site(request)
        subject = 'Account has been created, you can login now!'                  
                
        # load a template like get_template() 
        # and calls its render() method immediately.
        if self.email is not None:
            message = render_to_string('emails/account_activated.html', {
                'user': self,                    
                'domain': current_site.domain,
                
            })
            self.email_user(subject, message)

    
        
    
    @property
    def get_type(self):
        try:
            name = self.type.name
        except Exception as e:
            name = False            
        return name
    
    @property
    def expert_in_name(self):
        try:
            name = self.experts_in.name
        except Exception as e:
            name = False            
        return name
    
    @property
    def is_producer(self):
        if self.type.is_producer:
            return True
        return False
    
    
    @property
    def is_expert(self):
        if self.type.is_expert:
            return True
        return False
    
    @property
    def is_consumer(self):
        if self.type.is_consumer:
            return True
        return False
    
    def get_absolute_url(self):        
        return reverse('accounts:user_link', args=[str(self.username)])
    
    
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    established = models.DateField(null=True, blank=True)


