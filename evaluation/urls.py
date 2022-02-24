from django.urls import path
from . import views

app_name = 'evaluation'
urlpatterns = [
    path('evaluation/', views.eva_index, name='evaluation'),    
    path('evaluation/option_add/', views.option_add, name='option_add'),  
    path('evaluation/option_append/', views.option_append, name='option_append'),
    path('evaluation/thanks/', views.thanks, name='thanks'),      
    path('evaluation/report/<int:report_id>', views.report, name='report'),         
    
    
]