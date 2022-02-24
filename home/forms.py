from django import forms
from accounts.models import User, Profile
from evaluation.models import Question, Option

from django.contrib.auth.forms import PasswordChangeForm


class PasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget = forms.PasswordInput(attrs={'autocomplete': 'current-password', 'autofocus': True, 'class':'form-control'})
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class':'form-control'})
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class':'form-control'})
        





class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name', 'email', 'orgonization', 'phone', )
        
        widgets = {
                      
            'username': forms.TextInput(attrs={'placeholder': 'username', 'class':'form-control', 'aria-label':'username',  }),
            'first_name': forms.TextInput(attrs={'placeholder': 'first_name', 'class':'form-control', 'aria-label':'first_name' }),
            'last_name': forms.TextInput(attrs={'placeholder': 'last_name','class':'form-control', 'aria-label':'last_name', }), 
            'orgonization': forms.TextInput(attrs={'placeholder': 'orgonization','class':'form-control', 'aria-label':'orgonization', }), 
            'phone': forms.TextInput(attrs={'placeholder': 'phone','class':'form-control', 'aria-label':'phone', }), 
            'email': forms.EmailInput(attrs={'placeholder': 'email', 'class':'form-control', 'aria-label':'email' , }),
            
            
        }
        labels = {     
                     
            'username':'Username',
            'first_name':'First name',
            'first_name':'Last Name',
            'orgonization':'Orgonization',
            'phone':'Phone',
            'email': 'Email',
            
        }
        
        
   
        
class ProfileForm(forms.ModelForm):
    class Meta:
        
        
        model = Profile
        fields = ('about','location','established',)
        
        widgets = {
                      
            'about': forms.Textarea(attrs={'placeholder': 'about', 'class':'form-control', 'aria-label':'about' }),
            'location': forms.TextInput(attrs={'placeholder': 'location', 'class':'form-control', 'aria-label':'location' }),
            'established': forms.DateInput(attrs={'data-datepicker': "" , 'class':'form-control', 'aria-label':'established', }), 
            
            
        }
        labels = {     
                     
            'about': 'About',
            'location': 'Location',
            'established': 'Established',           
            
        }
        
class QuestionForm(forms.ModelForm):
    class Meta:
        model   = Question
        fields  = ('name',)
        widgets = {
                      
            'name': forms.TextInput(attrs={'placeholder': 'name', 'class':'form-control', 'aria-label':'name' }),          
            
            
        }
        
        labels = {     
                     
            'name': 'Edit Question',
            
                     
        }
        

class OptionForm(forms.ModelForm):
    class Meta:
        model   = Option
        fields  = ('name', 'statement', )
        widgets = {
                      
            'name': forms.TextInput(attrs={'placeholder': 'name', 'class':'form-control', 'aria-label':'name' }),
            'statement': forms.Textarea(attrs={'placeholder': 'statement', 'class':'form-control', 'aria-label':'statement' }),      
            
            
        }
        
        labels = {     
                     
            'name': 'Option Label',
            'statement': 'Option Statement',
                     
        }
        
    

        
       
  
  
        
  
  
       