from django.db import models

# A TBlock is the same as a block in the statechanges app, but used for
# different purposes and queries. Thereofor it's a seperated model.
class Tblock(models.Model):
    '''A model which describes a Block'''
    blocknumber = models.IntegerField(primary_key=True)
    date = models.DateTimeField()

class GETAddress(models.Model):
    '''A model which describes the GET address'''
    address = models.CharField(primary_key=True, max_length=100)
    balance = models.DecimalField(max_digits=26,decimal_places=18,default=0)
    lastupdate = models.DateTimeField(blank=True,null=True)

    def send(self, amount):
        self.balance = self.balance - amount
        self.save()

    def recieve(self, amount):
        self.balance = self.balance + amount
        self.save()

    def newupdate(self,date):
        self.lastupdate = date
        self.save()

class GETTransaction(models.Model):
    '''A model which decribes a transaction of the GET token'''
    transactionhash = models.CharField(max_length=100)
    fromaddress = models.ForeignKey(
        GETAddress,
        on_delete=models.CASCADE,
        related_name='fromtransaction'
    )
    toaddress = models.ForeignKey(
        GETAddress,
        on_delete=models.CASCADE,
        related_name='totransaction'
    )
    amount = models.DecimalField(max_digits=26,decimal_places=18)
    block = models.ForeignKey(
        Tblock,
        on_delete=models.CASCADE,
    )

class TAppStatus(models.Model):
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
