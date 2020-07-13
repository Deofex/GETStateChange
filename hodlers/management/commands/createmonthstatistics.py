from collections import defaultdict
from decimal import Decimal
from django.core.management.base import BaseCommand
from hodlers.models import GETTransaction, GETPeriodSummary

def create_monthstats(balances):
    # Zero out the holding of the addresses which shouldn't be part of the
    # rapport (SF address + burn address)
    excludeaddress = ["0x0000000000000000000000000000000000000000",
    "0x2408c65b811a4b51e426795d4f855b7b596b04d2",
    "0x08e41b9bd40a4e1d312379fdced8dac07665488c"
    ]
    for ea in excludeaddress:
        balances[ea] = 0

    # Store the amount of tokens which are stored on Exchanges
    etherdeltabalance = balances["0x8d12a197cb00d4747a1fe03395095ce2a5cc6819"]
    coinonebalance = balances["0x167a9333bf582556f35bd4d16a7e80e191aa6476"]
    idexbalance = balances["0x2a0c0dbecc7e4d658f48e01e3fa353f44050c208 "]
    liquidbalance = balances["0xedbb72e6b3cf66a792bff7faac5ea769fe810517"] + \
        balances["0xdf4b6fb700c428476bd3c02e6fa83e110741145b"]
    hotbitbalance = balances["0x274f3c32c90517975e29dfc209a23f315c1e5fc7"]
    uniswapbalance = balances["0x2680a95fc9de215f1034f073185cc1f2a28b4107 "]
    totalexchangebalance = etherdeltabalance + coinonebalance + idexbalance + \
        liquidbalance + hotbitbalance + uniswapbalance

    # Create a list from the hashtable and remove the addresses with less
    # than 5 tokens
    bottom_limit = Decimal("5")
    balances = {k: balances[k] for k in balances if balances[k] > bottom_limit}
    balances = [{"address": a, "amount": b} for a, b in balances.items()]
    balances = sorted(balances, key=lambda b: -abs(b["amount"]))

    output = {
        'activeaddresses':len(balances),
        'etherdeltabalance':coinonebalance,
        'coinonebalance':coinonebalance,
        'idexbalance' :idexbalance,
        'liquidbalance':liquidbalance,
        'hotbitbalance':hotbitbalance,
        'uniswapbalance':uniswapbalance,
        'totalexchangebalance':totalexchangebalance
    }

    return(output)

def collect_monthinfo():
    # Provide the month and year from where to start collecting
    month = 10
    year = 2017

    # Create Default dictionary, with a decimal number (0)
    balances = defaultdict(Decimal)

    # Create the burn address and add the amount of GET minted in it
    burnaddress = "0x0000000000000000000000000000000000000000"
    balances[burnaddress] = Decimal("33368773.400000170376363909")

    # Set the initial counters used to track the amount of transactions in a
    # period + the amount of GET involved in it
    transactioncount = 0
    transactionamountcount = 0

    for trans in GETTransaction.objects.order_by('block'):
        # If the month change, we have to collect information from the previous
        # month.
        if trans.block.date.month != month:
            # Create period name from the last collected period
            periodname = ("{}-{}".format(month,year))

            # Get the stats from the month
            periodinfo = create_monthstats(balances)

            # Print information about this stats
            print("------------{}---------------".format(periodname))
            print('Amount of transactions which found place: {}'.format(
                transactioncount
            ))
            print('Amount of GET transfered between wallets: {}'.format(
                transactionamountcount))
            print("Active addresses (more than 5 GET stored): {}".format(
                periodinfo["activeaddresses"]))
            print('Amount of GET stored on exchanges: {}'.format(
                periodinfo["totalexchangebalance"]
            ))

            # Set the month and year to the new block
            month = trans.block.date.month
            year = trans.block.date.year

            #Reset transactionCounts
            transactioncount = 0
            transactionamountcount = 0

        # Add 1 transaction to the counter
        transactioncount += 1
        transactionamountcount += + trans.amount

        # Add transaction amount to the TO address
        balances[trans.toaddress.address] = \
            balances[trans.toaddress.address] + trans.amount
        # Subtract transaction amount from the FROM address
        balances[trans.fromaddress.address] = \
            balances[trans.fromaddress.address] - trans.amount

    periodinfo = create_monthstats(balances)

# Base class, the start of each Django management command
class Command(BaseCommand):
    '''Import GET transactions stats in the database'''

    def handle(self, *args, **kwargs):
        collect_monthinfo()


#Monthinfo:
# +Amount of wallets with 5+ GET in it
# +Amount of transactions
# +Amount of GET transfered from 1 wallet to another
# +Amount of GET on the exchanges
# -On page (whale/guppies/dutchies etc.)