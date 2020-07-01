from collections import defaultdict
from decimal import Decimal
from django.core.management.base import BaseCommand
from hodlers.models import GETTransaction
import numpy

def create_monthstats(balances):
    # Zero out the holding of the addresses which shouldn't be part of the
    # rapport (SF address + burn address)
    excludeaddress = ["0x06d191c4bc47138d5d79eb881deea86c93e6603b",
        "0x08e41b9bd40a4e1d312379fdced8dac07665488c",
        "0x2408c65b811a4b51e426795d4f855b7b596b04d2",
        "0x0000000000000000000000000000000000000000",
        "0x2752cd55caf736de9da26e555f602cafecd81282",
        "0x36842c31d6e82d72139b42efc35f3d37de36da5e" ]

    for ea in excludeaddress:
        balances[ea] = 0

    # Create a list from the hashtable and remove the addresses with barely
    # any tokens
    bottom_limit = Decimal("1")
    balances = {k: balances[k] for k in balances if balances[k] > bottom_limit}
    balances = [{"address": a, "amount": b} for a, b in balances.items()]
    balances = sorted(balances, key=lambda b: -abs(b["amount"]))

    # Create a list with top 1000 addresses
    alladdresses = [balance['address'] for balance in balances]
    allvalues = [balance['amount'] for balance in balances]

    print(sum(allvalues))

    output = {
        'activeaddresses':len(alladdresses),
        'top100addresses':alladdresses[0:100],
        'top500addresses':alladdresses[0:500],
        'top1000addresses':alladdresses[0:1000],
        'mean':numpy.mean(allvalues),
        'top100valuesmean':numpy.mean(allvalues[0:100]),
        'top500valuesmean':numpy.mean(allvalues[0:500]),
        'top1000valuesmean':numpy.mean(allvalues[0:1000]),
        'median':numpy.median(allvalues),
        'top100valuesmedian':numpy.median(allvalues[0:100]),
        'top500valuesmedian':numpy.median(allvalues[0:500]),
        'top1000valuesmedian':numpy.median(allvalues[0:1000]),
    }

    return(output)

def collect_monthinfo():
    # Provide the month and year from where to start collecting
    month = 10
    year = 2017

    # Create Default dictionary, with a decimal number (0)
    balances = defaultdict(Decimal)
    burnaddress = "0x0000000000000000000000000000000000000000"
    balances[burnaddress] = Decimal("33368773.400000170376363909")
    for trans in GETTransaction.objects.all():
        # If the month change, we have to collect information from the previous
        # month.
        if trans.block.date.month != month:
            # Create period name
            periodname = ("{}-{}".format(month,year))

            # Get the stats from the month
            periodinfo = create_monthstats(balances)
            #TEMP------------->
            #for i in periodinfo:
            #    print ("{} - {}".format(i["address"], i["amount"]))
            #
            print ("------------{}---------------".format(periodname))
            print("Active addresses (more than 1 GET stored): {}".format(
                periodinfo["activeaddresses"]))
            print("Mean: {}".format(periodinfo["mean"]))
            print("Mean top 100: {}".format(periodinfo["top100valuesmean"]))
            print("Mean top 500: {}".format(periodinfo["top500valuesmean"]))
            print("Mean top 1000: {}".format(periodinfo["top1000valuesmean"]))
            print("Median: {}".format(periodinfo["median"]))
            print("Median top 100: {}".format(periodinfo["top100valuesmedian"]))
            print("Median top 500: {}".format(periodinfo["top500valuesmedian"]))
            print("Median top 1000: {}".format(periodinfo["top1000valuesmedian"]))
            #<---------ENDTEMP

            # Set the month and year to the new block
            month = trans.block.date.month
            year = trans.block.date.year

        # Add transaction amount to the TO address
        balances[trans.toaddress.address] = \
            balances[trans.toaddress.address] + trans.amount
        # Subtract transaction amount from the FROM address
        balances[trans.fromaddress.address] = \
            balances[trans.fromaddress.address] - trans.amount


# Base class, the start of each Django management command
class Command(BaseCommand):
    '''Import GET transactions stats in the database'''

    def handle(self, *args, **kwargs):
        collect_monthinfo()