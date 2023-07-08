from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Products)
admin.site.register(OrderItem)
admin.site.register(Orders)
admin.site.register(Tracking)
