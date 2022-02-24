from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = '__all__'
        
        
        
class UserCreationFormFront(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'type', 'experts_in')
        
        widgets = {
            'type': forms.Select(attrs={ 'class':'form-control', 'aria-label':'type', 'hx-post':"/check_type_to_get_expert/", 'hx-trigger':"change", 'hx-target':"#hx" , 'hx-swap':"innerHTML"}),                    
            'experts_in': forms.Select(attrs={ 'class':'form-control', 'aria-label':'experts_in' }),    
            'username': forms.TextInput(attrs={'placeholder': 'username', 'class':'form-control', 'aria-label':'username' }),
            'email': forms.EmailInput(attrs={'placeholder': 'your email', 'class':'form-control', 'aria-label':'email' }),
            
            
             
            
            
        }
        
        

class UserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'
        
