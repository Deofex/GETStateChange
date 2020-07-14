from datetime import datetime, timedelta

from django.shortcuts import render
from django.db.models import Avg, Sum
from .models import GETAddress, GETTransaction

from .graphinfohodlers import get_amountofhodlersgraphinfo, \
    get_amountoftransactionsgraphinfo, get_amountoftokensmovedgraphinfo, \
    get_tokensonexchangesgraphinfo, get_tokendistribution


# Page for hodler info
def page_hodlers(request):
    # List with walelts to exclude in queries (contract address + SF)
    ewl = ['0x0000000000000000000000000000000000000000',
           '0x2408c65b811a4b51e426795d4f855b7b596b04d2',
           '0x08e41b9bd40a4e1d312379fdced8dac07665488c'
           ]

    # Average of the addresses, without the earlier specified excludes
    average = GETAddress.objects.exclude(balance__lt=5).exclude(
        address__in=ewl).aggregate(Avg('balance'))['balance__avg']

    # GET Transactions last 24 hours
    yesterday = datetime.now() - timedelta(days=1)
    transactions24h = GETTransaction.objects.filter(
        block__date__gt=yesterday)
    transactions24hamount = transactions24h.count()
    transactions24htotal = transactions24h.aggregate(
        Sum('amount'))['amount__sum']

    # If the amount of transactions is None, change it to zero to prevent
    # the site not being displayed
    if transactions24htotal == None:
        transactions24htotal = 0

    return render(request, 'hodlers/hodlers.html', {
        'totalwalletamount': GETAddress.objects.exclude(balance__lte=5).count(),
        'averagegetperwallet': "{0:.0f}".format(average),
        'gettransactions24h': transactions24hamount,
        'gettransfered24h': "{0:.0f}".format(transactions24htotal),
        'amountofhodlers': get_amountofhodlersgraphinfo,
        'amountoftransactions': get_amountoftransactionsgraphinfo,
        'amountoftokensmoved': get_amountoftokensmovedgraphinfo,
        'tokenonexchanges': get_tokensonexchangesgraphinfo,
        'tokendistribution': get_tokendistribution,
        'navbar': 'page_hodlers',
    })
