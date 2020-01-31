from django.db import models
from django.utils import timezone


class Block(models.Model):
    '''Information about block'''
    blocknumber = models.IntegerField(primary_key=True)
    date = models.DateTimeField()
    fullyprocessed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.blocknumber)

# Create your models here.


class StateChange(models.Model):
    '''Summery of GET state changes which are posted hourly on the blockchain'''
    StateChangeTypes = (
        ('f', 'New firing'),
        ('w', 'New wiring'),
    )
    StateChangeSubTypes = (
        (0, 'Ticket or Wiring created'),
        (1, 'Ticket blocked'),
        (2, 'Ticket sold on primary market'),
        (3, 'Ticket sold on secondary market'),
        (4, 'Ticket bought back by organizer'),
        (5, 'Ticket cancelled'),
        (6, 'Ticket put for sale'),
        (7, 'Show cancelled'),
        (8, 'Ticket not resold'),
        (9, 'Ticket not sold on primary market'),
        (10, 'Ticket sold on the secondary market'),
        (11, 'Ticket scanned'),
        (12, 'Show over'),
        (13, 'Ticket unblocked'),
    )
    hash = models.CharField(
        max_length=100,
        primary_key=True,
    )
    previoushash = models.CharField(
        max_length=100,
    )
    statechangetype = models.CharField(
        max_length=1,
        choices=StateChangeTypes,
    )
    statechangesubtype = models.IntegerField(
        choices=StateChangeSubTypes,
    )
    block = models.ForeignKey(
        Block,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return str(self.hash)

class CryptoPrice(models.Model):
    '''The price of a cryptotoken in different valuta'''
    name = models.CharField(
        max_length=3
    )
    price_eur = models.FloatField()

    def updateeurprice(self, price):
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
