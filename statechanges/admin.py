from django.contrib import admin
from .models import Block, StateChange, CryptoPrice, BurnTransaction, Event

# Register your models here.
admin.site.register(Block)
admin.site.register(Event)
admin.site.register(StateChange)
admin.site.register(CryptoPrice)
admin.site.register(BurnTransaction)