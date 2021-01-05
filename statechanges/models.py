from django.db import models
from django.utils import timezone
# Configure logger
import logging
logger = logging.getLogger(__name__)


class Block(models.Model):
    '''Information about block'''
    blocknumber = models.IntegerField(primary_key=True)
    date = models.DateTimeField()
    fullyprocessed = models.BooleanField(default=False)
    ipfshash = models.CharField(
        blank=True,
        max_length=100,
    )
    # The sums of the firings in the event. (Those can be retrieved from the)
    # underlying statechanges, but this cost to much performance when
    # dynamically requested.
    f0sum = models.IntegerField(default=0)
    f1sum = models.IntegerField(default=0)
    f2sum = models.IntegerField(default=0)
    f3sum = models.IntegerField(default=0)
    f4sum = models.IntegerField(default=0)
    f5sum = models.IntegerField(default=0)
    f6sum = models.IntegerField(default=0)
    f7sum = models.IntegerField(default=0)
    f8sum = models.IntegerField(default=0)
    f9sum = models.IntegerField(default=0)
    f10sum = models.IntegerField(default=0)
    f11sum = models.IntegerField(default=0)
    f12sum = models.IntegerField(default=0)
    f13sum = models.IntegerField(default=0)
    f999sum = models.IntegerField(default=0)
    wsum = models.IntegerField(default=0)
    totalsum = models.IntegerField(default=0)

    # Multiple function to increase the firings and total sum
    def add_f0(self):
        self.f0sum = self.f0sum + 1
        self.totalsum = self.totalsum + 1
        self.save()

    def add_f1(self):
        self.f1sum = self.f1sum + 1
        self.totalsum = self.totalsum + 1
        self.save()

    def add_f2(self):
        self.f2sum = self.f2sum + 1
        self.totalsum = self.totalsum + 1
        self.save()

    def add_f3(self):
        self.f3sum = self.f3sum + 1
        self.totalsum = self.totalsum + 1
        self.save()

    def add_f4(self):
        self.f4sum = self.f4sum + 1
        self.totalsum = self.totalsum + 1
        self.save()

    def add_f5(self):
        self.f5sum = self.f5sum + 1
        self.totalsum = self.totalsum + 1
        self.save()

    def add_f6(self):
        self.f6sum = self.f6sum + 1
        self.totalsum = self.totalsum + 1
        self.save()

    def add_f7(self):
        self.f7sum = self.f7sum + 1
        self.totalsum = self.totalsum + 1
        self.save()

    def add_f8(self):
        self.f8sum = self.f8sum + 1
        self.totalsum = self.totalsum + 1
        self.save()

    def add_f9(self):
        self.f9sum = self.f9sum + 1
        self.totalsum = self.totalsum + 1
        self.save()

    def add_f10(self):
        self.f10sum = self.f10sum + 1
        self.totalsum = self.totalsum + 1
        self.save()

    def add_f11(self):
        self.f11sum = self.f11sum + 1
        self.totalsum = self.totalsum + 1
        self.save()

    def add_f12(self):
        self.f12sum = self.f12sum + 1
        self.totalsum = self.totalsum + 1
        self.save()

    def add_f13(self):
        self.f13sum = self.f13sum + 1
        self.totalsum = self.totalsum + 1
        self.save()

    def add_f999(self):
        self.f999sum = self.f999sum + 1
        self.totalsum = self.totalsum + 1
        self.save()

    def add_w(self):
        self.wsum = self.wsum + 1
        self.totalsum = self.totalsum + 1
        self.save()

    def processed(self):
        self.fullyprocessed = True
        self.save()

    def addipfshash(self,ipfshash):
        self.ipfshash = ipfshash
        self.save()

    def __str__(self):
        return str(self.blocknumber)


class Event(models.Model):
    '''A model which describes an Event'''
    # The hash is the primary key
    hash = models.CharField(
        max_length=100,
        primary_key=True,
    )
    # The name of the event (can be empty)
    name = models.CharField(
        blank=True,
        max_length=100,
    )
    # The block were the event is created
    block = models.ForeignKey(
        Block,
        on_delete=models.CASCADE,
    )

    lastupdate = models.DateTimeField(
        default=timezone.now
    )

    # The sums of the firings in the event. (Those can be retrieved from the)
    # underlying statechanges, but this cost to much performance when
    # dynamically requested.
    f0sum = models.IntegerField(default=0)
    f1sum = models.IntegerField(default=0)
    f2sum = models.IntegerField(default=0)
    f3sum = models.IntegerField(default=0)
    f4sum = models.IntegerField(default=0)
    f5sum = models.IntegerField(default=0)
    f6sum = models.IntegerField(default=0)
    f7sum = models.IntegerField(default=0)
    f8sum = models.IntegerField(default=0)
    f9sum = models.IntegerField(default=0)
    f10sum = models.IntegerField(default=0)
    f11sum = models.IntegerField(default=0)
    f12sum = models.IntegerField(default=0)
    f13sum = models.IntegerField(default=0)
    f999sum = models.IntegerField(default=0)
    totalsum = models.IntegerField(default=0)

    # Multiple function to increase the firings and total sum
    def add_f0(self,updatedate):
        self.f0sum = self.f0sum + 1
        self.totalsum = self.totalsum + 1
        if self.lastupdate < updatedate:
            self.lastupdate = updatedate
        self.save()

    def add_f1(self,updatedate):
        self.f1sum = self.f1sum + 1
        self.totalsum = self.totalsum + 1
        if self.lastupdate < updatedate:
            self.lastupdate = updatedate
        self.save()

    def add_f2(self,updatedate):
        self.f2sum = self.f2sum + 1
        self.totalsum = self.totalsum + 1
        if self.lastupdate < updatedate:
            self.lastupdate = updatedate
        self.save()

    def add_f3(self,updatedate):
        self.f3sum = self.f3sum + 1
        self.totalsum = self.totalsum + 1
        if self.lastupdate < updatedate:
            self.lastupdate = updatedate
        self.save()

    def add_f4(self,updatedate):
        self.f4sum = self.f4sum + 1
        self.totalsum = self.totalsum + 1
        if self.lastupdate < updatedate:
            self.lastupdate = updatedate
        self.save()

    def add_f5(self,updatedate):
        self.f5sum = self.f5sum + 1
        self.totalsum = self.totalsum + 1
        if self.lastupdate < updatedate:
            self.lastupdate = updatedate
        self.save()

    def add_f6(self,updatedate):
        self.f6sum = self.f6sum + 1
        self.totalsum = self.totalsum + 1
        if self.lastupdate < updatedate:
            self.lastupdate = updatedate
        self.save()

    def add_f7(self,updatedate):
        self.f7sum = self.f7sum + 1
        self.totalsum = self.totalsum + 1
        if self.lastupdate < updatedate:
            self.lastupdate = updatedate
        self.save()

    def add_f8(self,updatedate):
        self.f8sum = self.f8sum + 1
        self.totalsum = self.totalsum + 1
        if self.lastupdate < updatedate:
            self.lastupdate = updatedate
        self.save()

    def add_f9(self,updatedate):
        self.f9sum = self.f9sum + 1
        self.totalsum = self.totalsum + 1
        if self.lastupdate < updatedate:
            self.lastupdate = updatedate
        self.save()

    def add_f10(self,updatedate):
        self.f10sum = self.f10sum + 1
        self.totalsum = self.totalsum + 1
        if self.lastupdate < updatedate:
            self.lastupdate = updatedate
        self.save()

    def add_f11(self,updatedate):
        self.f11sum = self.f11sum + 1
        self.totalsum = self.totalsum + 1
        if self.lastupdate < updatedate:
            self.lastupdate = updatedate
        self.save()

    def add_f12(self,updatedate):
        self.f12sum = self.f12sum + 1
        self.totalsum = self.totalsum + 1
        if self.lastupdate < updatedate:
            self.lastupdate = updatedate
        self.save()

    def add_f13(self,updatedate):
        self.f13sum = self.f13sum + 1
        self.totalsum = self.totalsum + 1
        if self.lastupdate < updatedate:
            self.lastupdate = updatedate
        self.save()

    def add_f999(self,updatedate):
        self.f999sum = self.f999sum + 1
        self.totalsum = self.totalsum + 1
        if self.lastupdate < updatedate:
            self.lastupdate = updatedate
        self.save()

    def __str__(self):
        return str(self.hash)

class Ticket(models.Model):
    '''A single ticket contain multiple statechanges'''
    # The hash of the ticket (firing 0 hash)
    hash = models.CharField(
        max_length=100,
        primary_key=True,
    )
    # The event which correspond to the ticket
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
    )

    # The last update time of the ticket
    lastupdate = models.DateTimeField(
        default=timezone.now
    )

    def updatetime(self,updatedate):
        if self.lastupdate < updatedate:
            self.lastupdate = updatedate
            self.save()

    def __str__(self):
        return str(self.hash)

class StateChange(models.Model):
    '''Summery of GET state changes which are posted hourly on the blockchain'''
    class Meta:
        ordering = ['block']
    firingtypes = (
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
        (999, 'Error'),
    )
    hash = models.CharField(
        max_length=100,
        primary_key=True,
    )
    previoushash = models.CharField(
        max_length=100,
    )
    firing = models.IntegerField(
        choices=firingtypes,
    )
    block = models.ForeignKey(
        Block,
        on_delete=models.CASCADE,
    )
    ticket = models.ForeignKey(
        Ticket,
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
        logger.info("Price will be updated.")
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

class AppStatus(models.Model):
    '''Add statusses which the application use during the runtime'''
    name = models.CharField(
        max_length=100,
        primary_key=True,
    )
    status = models.BooleanField()

    def enablestatus(self):
        self.status = True
        self.save()

    def disablestatus(self):
        self.status = False
        self.save()

    def __str__(self):
        return str(self.name)