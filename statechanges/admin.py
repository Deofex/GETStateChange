from django.contrib import admin
from .models import StateChange
from .models import CryptoPrice

# Register your models here.
admin.site.register(StateChange)
admin.site.register(CryptoPrice)