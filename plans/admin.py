from django.contrib import admin
from plans.models import FitnessPlan, Customer

# Register your models here.
admin.site.register(FitnessPlan)
admin.site.register(Customer)