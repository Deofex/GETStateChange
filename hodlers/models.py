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
    balance = models.DecimalField(max_digits=26, decimal_places=18, default=0)
    lastupdate = models.DateTimeField(blank=True, null=True)

    def send(self, amount):
        self.balance = self.balance - amount
        self.save()

    def recieve(self, amount):
        self.balance = self.balance + amount
        self.save()

    def newupdate(self, date):
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
    amount = models.DecimalField(max_digits=26, decimal_places=18)
    block = models.ForeignKey(
        Tblock,
        on_delete=models.CASCADE,
    )


class GETPeriodSummary(models.Model):
    '''A model which stores data about the GET tokens for a period'''
    periodname = models.CharField(primary_key=True, max_length=100)
    activewallets = models.IntegerField()
    transactions = models.IntegerField()
    getdistributed = models.DecimalField(max_digits=12, decimal_places=2)
    exetherdeltabalance = models.DecimalField(max_digits=12, decimal_places=2)
    excoinonebalance = models.DecimalField(max_digits=12, decimal_places=2)
    exidexbalance = models.DecimalField(max_digits=12, decimal_places=2)
    exliquidbalance = models.DecimalField(max_digits=12, decimal_places=2)
    exuniswapbalance = models.DecimalField(max_digits=12, decimal_places=2)
    exhotbitbalance = models.DecimalField(max_digits=12, decimal_places=2)
    extotalbalance = models.DecimalField(max_digits=12, decimal_places=2)
    fullyprocessed = models.BooleanField()

    def update(self, activewallets, transactions, getdistributed,
               exetherdeltabalance, excoinonebalance, exidexbalance,
               exliquidbalance, exuniswapbalance, exhotbitbalance,
               extotalbalance,fullyprocessed):
        if activewallets != self.activewallets:
            self.activewallets = activewallets
        if transactions != self.transactions:
            self.transactions = transactions
        if getdistributed != self.getdistributed:
            self.getdistributed = getdistributed
        if exetherdeltabalance != self.exetherdeltabalance:
            self.exetherdeltabalance = exetherdeltabalance
        if excoinonebalance != self.excoinonebalance:
            self.excoinonebalance = excoinonebalance
        if exidexbalance != self.exidexbalance:
            self.exidexbalance = exidexbalance
        if exliquidbalance != self.exliquidbalance:
            self.exliquidbalance = exliquidbalance
        if exuniswapbalance != self.exuniswapbalance:
            self.exuniswapbalance = exuniswapbalance
        if exhotbitbalance != self.exhotbitbalance:
            self.exhotbitbalance = exhotbitbalance
        if extotalbalance != self.extotalbalance:
            self.extotalbalance = extotalbalance
        if fullyprocessed != self.fullyprocessed:
            self.fullyprocessed = fullyprocessed
        self.save()


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
