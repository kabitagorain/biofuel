from django.db import models
from django_countries.fields import CountryField
import random

def random_digits():
    return "%0.12d" % random.randint(0, 999999999999)

class Lead(models.Model):
    lead = models.CharField(max_length=256)
    email_address = models.EmailField(unique=True)
    phone = models.CharField(max_length=256)
    address_1 = models.CharField(max_length=256)
    address_2 = models.CharField(max_length=256)
    city = models.CharField(max_length=256)
    country = CountryField()
    subscribed = models.BooleanField(default=True)
    confirm_code = models.CharField(max_length=50, default=random_digits())
    
    def __str__(self):
        return self.lead
