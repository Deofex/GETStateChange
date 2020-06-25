from datetime import datetime, timedelta

from django.shortcuts import render
from django.db.models import Avg, Sum
from .models import GETAddress, GETTransaction


# Page for hodler info
def page_hodlers(request):
    # List with walelts to exclude in queries (contract address + SF)
    ewl = ['0x0000000000000000000000000000000000000000',
    '0x2408c65b811a4b51e426795d4f855b7b596b04d2']

    # Average of the addresses, without the earlier specified excludes
    average = GETAddress.objects.exclude(balance__lt=1).exclude(
        address__in=ewl).aggregate(Avg('balance'))['balance__avg']

    # GET Transactions last 24 hours
    yesterday = datetime.now() - timedelta(days=1)
    transactions24h = GETTransaction.objects.filter(
        block__date__gt=yesterday)

    transactions24hamount = transactions24h.count()
    transactions24htotal = transactions24h.aggregate(
        Sum('amount'))['amount__sum']


    return render(request, 'hodlers/hodlers.html', {
        'totalwalletamount': GETAddress.objects.exclude(balance__lt=1).count(),
        'averagegetperwallet': "{0:.0f}".format(average),
        'gettransactions24h': transactions24hamount,
        'gettransfered24h': "{0:.0f}".format(transactions24htotal),
    })
