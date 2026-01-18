from django.contrib import admin
from hospital.models import *
# Register your models here.

admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Hospital)

