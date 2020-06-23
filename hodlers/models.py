from django.db import models

# A TBlock is the same as a block in the statechanges app, but used for
# different purposes and queries. Thereofor it's a seperated model.
class Tblock(models.Model):
    '''A model which describes a Block'''
    blocknumber = models.IntegerField(primary_key=True)
    date = models.DateTimeField()

class GETAddress(model.Models):
    '''A model which describes the GET address'''
    address = models.CharField(primary_key=True, max_length=100)

class GETTransaction(models.Model):
    '''A model which decribes a transaction of the GET token'''
    transactionhash = models.CharField(primary_key=True, max_length=100)
    fromaddress = models.ForeignKey(
        GETAddress,
        on_delete=models.CASCADE,
    )
    toaddress = models.ForeignKey(
        GETAddress,
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(max_digits=26,decimal_places=18)
    block = models.ForeignKey(
        Tblock,
        on_delete=models.CASCADE,
    )
