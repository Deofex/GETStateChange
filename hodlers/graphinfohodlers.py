from .models import GETPeriodSummary, GETAddress
from datetime import datetime

# create a graph class where to store periods and a single value
class GraphInfo():
    def __init__(self,periodname,value):
        self.periodname = periodname
        self.value = value

def get_amountofhodlersgraphinfo():
    '''Create the graph info for the amount of hodlers through the time'''
    # Create an empty list to store the graph info in
    graphinfo = []

    # Process each period
    periods = GETPeriodSummary.objects.all()

    for period in periods:
        # Create the label from the date in the following format day-month-year
        periodname = period.periodname.strftime("%m-%Y")
        graphinfo.append(GraphInfo(
            periodname,
            period.activewallets
        ))

    return graphinfo


def get_amountoftransactionsgraphinfo():
    '''Create the graph info for the amount of hodlers through the time'''
    # Create an empty list to store the graph info in
    graphinfo = []

    # Process each period
    periods = GETPeriodSummary.objects.all()

    excludebefore = datetime(2018,12,1)
    for period in periods:
        # Exclude period before 2019
        if period.periodname <= excludebefore:
            continue
        # Create the label from the date in the following format day-month-year
        periodname = period.periodname.strftime("%m-%Y")
        graphinfo.append(GraphInfo(
            periodname,
            period.transactions
        ))

    return graphinfo

def get_amountoftokensmovedgraphinfo():
    '''Create the graph info for the amount of hodlers through the time'''
    # Create an empty list to store the graph info in
    graphinfo = []

    # Process each period
    periods = GETPeriodSummary.objects.all()

    excludebefore = datetime(2018,12,1)
    for period in periods:
        # Exclude period before 2019
        if period.periodname <= excludebefore:
            continue
        # Create the label from the date in the following format day-month-year
        periodname = period.periodname.strftime("%m-%Y")
        graphinfo.append(GraphInfo(
            periodname,
            "{0:.0f}".format(period.getdistributed)
        ))

    return graphinfo

def get_tokensonexchangesgraphinfo():
    '''Create the graph info for the amount of hodlers through the time'''
    # Create an empty list to store the graph info in
    graphinfo = []

    # Process each period
    periods = GETPeriodSummary.objects.all()

    for period in periods:
        # Create the label from the date in the following format day-month-year
        periodname = period.periodname.strftime("%m-%Y")
        graphinfo.append(GraphInfo(
            periodname,
            "{0:.0f}".format(period.extotalbalance)
        ))

    return graphinfo

def get_tokendistribution():
    # Get the amount of wallets with:
    # 100k plus - 50k-100k - 10k-50k - 1k-10k - 100-1k 5-100
    htplus = GETAddress.objects.filter(balance__gt=100000).count()
    fkhk = GETAddress.objects.filter(balance__range=[50000,99999]).count()
    tkfk = GETAddress.objects.filter(balance__range=[10000,49999]).count()
    oktk = GETAddress.objects.filter(balance__range=[1000,9999]).count()
    hok = GETAddress.objects.filter(balance__range=[100,999]).count()
    fh = GETAddress.objects.filter(balance__range=[5,99]).count()

    graphinfo = [
        GraphInfo('100k plus', htplus),
        GraphInfo('50k-100k',fkhk),
        GraphInfo('10k-50k',tkfk),
        GraphInfo('1k-10k',oktk),
        GraphInfo('100-1k',hok),
        GraphInfo('5-100',fh),
    ]

    return graphinfo