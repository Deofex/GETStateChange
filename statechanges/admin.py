from django.contrib import admin
from .models import StateChange
from .models import CryptoPrice
from .models import BurnTransaction

# Register your models here.
admin.site.register(StateChange)
admin.site.register(CryptoPrice)
admin.site.register(BurnTransaction)