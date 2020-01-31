from django.db import models
from django.utils import timezone

class Block(models.Model):
    '''Information about block'''
    blocknumber = models.IntegerField(primary_key=True)
    date = models.DateTimeField()

    def __str__(self):
        return str(self.blocknumber)

# Create your models here.
class StateChange(models.Model):
    '''Summery of GET state changes which are posted hourly on the blockchain'''
    StateChangeTypes = (
        ('f0', 'Ticket created'),
        ('f1', 'Ticket blocked'),
        ('f2', 'Ticket sold on primary market'),
        ('f3', 'Ticket sold on secondary market'),
        ('f4', 'Ticket bought back by organizer'),
        ('f5', 'Ticket cancelled'),
        ('f6', 'Ticket put for sale'),
        ('f7', 'Show cancelled'),
        ('f8', 'Ticket not resold'),
        ('f9', 'Ticket not sold on primary market'),
        ('f10', 'Ticket sold on the secondary market'),
        ('f11', 'Ticket scanned'),
        ('f12', 'Show over'),
        ('f13', 'Ticket unblocked'),
        ('w', 'New wiring'),
    )
    hash = models.CharField(
        max_length=100,
        primary_key=True,
    )
    previoushash = models.CharField(
        max_length=100,
    )
    statechangetype = models.CharField(
        max_length =3,
        choices = StateChangeTypes
    )
    block = models.ForeignKey(
        Block,
        on_delete=models.CASCADE
    )

class CryptoPrice(models.Model):
    '''The price of a cryptotoken in different valuta'''
    name = models.CharField(
        max_length=3
    )
    price_eur = models.FloatField()

    def updateeurprice(self,price):
        self.price_eur = price
        print("Price will be updated.")
        self.save()

    def __str__(self):
        return self.name

class BurnTransaction(models.Model):
    '''A transaction send to the burn address'''
    date = models.DateTimeField()
    blocknumber = models.IntegerField()
    getburned = models.FloatField()

    def __str__(self):
        return str(self.blocknumber)
