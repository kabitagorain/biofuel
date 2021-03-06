from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.sites.models import Site
from .forms import UserCreationForm, UserChangeForm
from .models import User, UserType
from django.contrib import messages
from django.utils.translation import ngettext




class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ['type', 'experts_in', 'email', 'username', 'is_staff', 'is_active',]
    
    list_filter = ('type', 'is_active', 'is_staff', 'experts_in',)
    search_fields = ('email', 'phone', 'orgonization', 'username', 'experts_in', )
    
    fieldsets =  (
        (None, {'fields': ('type', 'experts_in',)}),
    ) + UserAdmin.fieldsets 
    
    @admin.action(description='Activate selected account and send mail')
    def activate_account(self, request, queryset):
        updated = queryset.update(is_active= True)
        self.message_user(request, ngettext(
            '%d User was successfully marked as active.',
            '%d Users were successfully marked as active.',
            updated,
        ) % updated, messages.SUCCESS)
        for user in queryset:
            user.send_active_mail(request)
        
    @admin.action(description='Deactivate selected account')
    def deactivate_account(self, request, queryset):
        updated = queryset.update(is_active= False)
        self.message_user(request, ngettext(
            '%d User was successfully marked as deactive.',
            '%d Users were successfully marked as deactive.',
            updated,
        ) % updated, messages.SUCCESS)
        
    @admin.action(description='Send mail to the domain expert to update feedback ')
    def send_mail_to_expert(self, request, queryset):
        user_type = []
        for i in queryset:
            user_type.append(i.type.is_expert)
        if False in user_type:
            return self.message_user(request, "Non Expert Selected! Please select experts only!")      
        
        from django.template.loader import render_to_string
        from django.core.mail import send_mass_mail
        current_site = Site.objects.get_current()
        subject = 'Question updated!'    
        message = render_to_string('emails/expert_mail.html', {                        
            'domain': current_site.domain,            
            })  
        mail_to_expert = [(subject, message, 'from@example.com', [obj.email]) for obj in queryset]
        send_mass_mail((mail_to_expert), fail_silently=False) 
        self.message_user(request, "Mail sent successfully ")
        
    actions = [activate_account, deactivate_account, send_mail_to_expert]

admin.site.register(User, UserAdmin)


@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = [f.name for f in UserType._meta.fields if f.editable and not f.name == "id"] 
    list_filter = ('name', )
    search_fields = ('name', )
    prepopulated_fields = {'slug': ('name',)}   
    ordering = ('name',)
    
    

    