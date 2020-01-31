from django.shortcuts import render
from .models import Block
from .models import StateChange
from .models import CryptoPrice
from .models import BurnTransaction
from django.core.paginator import Paginator
from datetime import datetime
from datetime import timedelta

class TimeRange():
    def __init__(self,startdate,enddate):
        self.startdate = startdate
        self.enddate = enddate

class GraphInfo():
    def __init__(self,periodname,value):
        self.periodname = periodname
        self.value = value

class DoubleGraphInfo(GraphInfo):
    def __init__(self, periodname, value, secondvalue):
        super().__init__(periodname, value)
        self.secondvalue = secondvalue

class statechangebatchinfo():
    def __init__(self,block,
    f0,f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,wirings,sum):
        self.block = block
        self.f0 = f0
        self.f1 = f1
        self.f2 = f2
        self.f3 = f3
        self.f4 = f4
        self.f5 = f5
        self.f6 = f6
        self.f7 = f7
        self.f8 = f8
        self.f9 = f9
        self.f10 = f10
        self.f11 = f11
        self.f12 = f12
        self.f13 = f13
        self.wirings = wirings
        self.sum = sum

def get_paginationnrs(page,paginatormaxnr):
    currentpage = int(page)
    if (currentpage + 7) > paginatormaxnr:
        maxpage = paginatormaxnr + 1
    else:
        maxpage = currentpage + 7

    # Set the temporary range to the current page, to the max page
    pagenrs = range(currentpage,maxpage)

    if (len(pagenrs) < 4):
        if (currentpage - (8 - len(pagenrs))) < 1:
            minpage = 1
        else:
            minpage = currentpage - (8 - len(pagenrs))
    elif (currentpage - 3) < 1:
        minpage = 1
    else:
        minpage = currentpage - 3

    pagenrs = range(minpage,maxpage)

    if len(pagenrs) > 7:
        pagenrs = pagenrs[:7]

    return pagenrs


# This function provide 12 timeranges (one range is one month)
# One timerange is a month from the beginning until the end of a calendar month
def get_monthtimerange():
    # Get the current year and month
    currentmonth = datetime.now().month
    currentyear = datetime.now().year
    # Create a list where to store the date ranges (this will be returned)
    timeranges = []
    # The Startdate of the first timerange is the first day of the current month
    startdate = datetime(currentyear,currentmonth,1)
    # Determine the first day of the next month and save this
    if currentmonth == 12:
        enddate = datetime((currentyear + 1), 1, 1)
    else:
        enddate = datetime(currentyear,(currentmonth + 1),1)
    # Combine the start and end date and add this in the timeranges list
    timeranges.append(TimeRange(
        startdate,
        enddate - timedelta(seconds=1)
    ))
    # Determine the other 11 timezones bij doing the same as the first month
    # but go back in time one month each time.
    for i in range(1,12):
        enddate = datetime(currentyear, currentmonth, 1)
        if currentmonth == 1:
            currentmonth = 12
            currentyear = currentyear - 1
        else:
            currentmonth = currentmonth - 1
        startdate = datetime(currentyear,(currentmonth ),1)
        timeranges.append(TimeRange(
            startdate,
            enddate - timedelta(seconds=1)
        ))
    # Reverse the list
    timeranges.reverse()
    # Return the timeranges
    return timeranges

def get_quartertimerange():
    # Get the current year and month
    date = datetime.now()
    currentmonth = datetime.now().month
    currentyear = datetime.now().year
    # Create a list where to store the date ranges (this will be returned)
    timeranges = []

    # Get the last 12 quarters
    for x in range(12):
        if date.month < 4:
            startdate = datetime(date.year, 1, 1)
            enddate = datetime(date.year, 3, 31, 23, 59, 59)
        elif date.month < 7:
            startdate = datetime(date.year, 4, 1)
            enddate = datetime(date.year, 6, 30, 23, 59, 59)
        elif date.month < 10:
            startdate = datetime(date.year, 7, 1)
            enddate = datetime(date.year, 9, 30, 23, 59, 59)
        else:
            startdate = datetime(date.year, 10, 1)
            enddate = datetime(date.year, 12, 31, 23, 59, 59)

        # Add the quarter to the timerange
        timeranges.append(TimeRange(
            startdate,
            enddate - timedelta(seconds=1)
        ))
        # Set the date to a previous quarter (1 seconds before the start time)
        # to let the next run get the previous quarter dates.
        date = startdate - timedelta(seconds=1)

    # Reverse the list
    timeranges.reverse()
    # Return the timeranges
    return timeranges

# This function creates the info for the monthly statechanges graph
def get_monthgraphinfo():
    # Get the last 12 time ranges
    timeranges = get_monthtimerange()
    # Create an empty list to store the graph info in
    graphinfo = []
    # Foreach timerange retrieve the amount of statechanges and translate the
    # month number and save both in the created list and return this object.
    for timerange in timeranges:
        # Get all statechanges in the timerange
        sumstatechanges = StateChange.objects.filter(
            block__date__range=[timerange.startdate,timerange.enddate]).count()

        # Create the label from the date in the following format day-month-year
        label = timerange.startdate.strftime("%d-%m-%Y")

        # Add the sum of the state changes and period name in an object and add
        # this to the list
        if sumstatechanges != 0:
            graphinfo.append(GraphInfo(
                label,
                sumstatechanges
            ))

    # Return the list with the graph info
    return graphinfo

# This function creates the info for the quarter statechanges graph
def get_quartergraphinfo():
    # Get the last 12 time ranges
    timeranges = get_quartertimerange()
    # Create an empty list to store the graph info in
    graphinfo = []
    # Foreach timerange retrieve the amount of statechanges and translate the
    # month number and save both in the created list and return this object.
    for timerange in timeranges:
        # Get all statechanges in the timerange
        sumstatechanges = StateChange.objects.filter(
            block__date__range=[timerange.startdate,timerange.enddate]).count()

        # Create the label from the date in the following format day-month-year
        label = timerange.startdate.strftime("%d-%m-%Y")

        # Add the sum of the state changes and period name in an object and add
        # this to the list
        if sumstatechanges != 0:
            graphinfo.append(GraphInfo(
                label,
                sumstatechanges
            ))

    # Return the list with the graph info
    return graphinfo


# This function creates the info for the daily statechanges graph
def get_daygraphinfo():
    currentday = datetime.now().day
    currentmonth = datetime.now().month
    currentyear = datetime.now().year
    startdate = datetime(currentyear,currentmonth,currentday)
    enddate = startdate + timedelta(days=1)
    graphinfo = []
    for i in range(1,31):
        # Get all statechanges batches in the timerange
        sumstatechanges = StateChange.objects.filter(
            block__date__range=[startdate,enddate]).count()

        # Create the label from the date in the following format day-month-year
        label = startdate.strftime("%d-%m-%Y")

        # Add the period to the graphinfo
        graphinfo.append(GraphInfo(
            label,
            sumstatechanges
        ))

        # Go back in time 1 day for the next run
        startdate = startdate - timedelta(days=1)
        enddate = enddate - timedelta(days=1)

    # Reverse the list created to get the oldest date on top
    graphinfo.reverse()

    # Return the list with the graph info
    return graphinfo

# This function creates the info for the daily wiring graph
def get_wiringgraphinfo():
    currentday = datetime.now().day
    currentmonth = datetime.now().month
    currentyear = datetime.now().year
    startdate = datetime(currentyear,currentmonth,currentday)
    enddate = startdate + timedelta(days=1)
    graphinfo = []
    for i in range(1,31):
        # Get all statechanges batches in the timerange
        sumstatechanges = StateChange.objects.filter(
            block__date__range=[startdate,enddate]).count()

        # Create the label from the date in the following format day-month-year
        label = startdate.strftime("%d-%m-%Y")

        # Add the period to the graphinfo
        graphinfo.append(GraphInfo(
            label,
            sumstatechanges
        ))

        # Go back in time 1 day for the next run
        startdate = startdate - timedelta(days=1)
        enddate = enddate - timedelta(days=1)

    # Reverse the list created to get the oldest date on top
    graphinfo.reverse()

    # Return the list with the graph info
    return graphinfo

# Get the state changes from the last 30 days
def get_statechangetypeslast30days():
    #Determine the start and
    currentday = datetime.now().day
    currentmonth = datetime.now().month
    currentyear = datetime.now().year
    enddate = datetime(currentyear,currentmonth,currentday)
    startdate = enddate - timedelta(days=30)
    # Get all statebatches from the last 30 days
    statechangefirings = StateChange.objects.filter(
        block__date__range=[startdate,enddate],statechangetype='f')
    # Create an empty array
    graphinfo = []
    # Cycle through 0 to 13 (amount of state changes)
    for i in range(0,14):
        # Get the amount of state changes of the type firings + i
        statechangefirings = StateChange.objects.filter(
            block__date__range=[startdate,enddate],
            statechangetype='f',
            statechangesubtype=i).count()

        # Get the label of the firing
        nameconvert = {
            0: "Tickets created",
            1: "Tickets blocked",
            2: "Tickets sold in the primary market",
            3: "Tickets sold in secondary market",
            4: "Tickets bought back",
            5: "Tickets cancelled",
            6: "Ticket put for sale",
            7: "No Show",
            8: "Not resold",
            9: "Not sold in primary market",
            10: "Not sold in secondary market",
            11: "Tickets scanned",
            12: "Show over",
            13: "Tickets unblocked"
        }
        label = nameconvert.get(i, "Unknown")

        # If more than 0 statechanges of the specific type occured, add it to
        # the array
        if statechangefirings != 0:
            graphinfo.append(GraphInfo(
                label,
                statechangefirings
            ))
    # Return the array
    return graphinfo


def get_burngraphinfo():
    # Total GET supply is 33,368,773
    totalsupply = 33368773
    supply = totalsupply
    # Create an empty array
    graphinfo = []
    #Add each burntransaction to the array
    for transaction in BurnTransaction.objects.all():
        # Create the label from the date in the following format day-month-year
        label = transaction.date.strftime("%d-%m-%Y")
        # Supply = Supply - the amount of GET burned
        supply = supply - transaction.getburned
        procentburned = (totalsupply - supply) / (supply / 100)
        #Add the graph information
        graphinfo.append(DoubleGraphInfo(
                label,
                "{0:.0f}".format(supply),
                "{0:.2f}".format(procentburned)
            ))
    return graphinfo

def get_statechangestatistics(blocks):
    statechangestatistics = []
    for block in blocks:
        statechangestatistics.append(statechangebatchinfo(
            block=block,
            f0 = StateChange.objects.filter(
                block=block,statechangetype="f",statechangesubtype=0).count(),
            f1 = StateChange.objects.filter(
                block=block,statechangetype="f",statechangesubtype=1).count(),
            f2 = StateChange.objects.filter(
                block=block,statechangetype="f",statechangesubtype=2).count(),
            f3 = StateChange.objects.filter(
                block=block,statechangetype="f",statechangesubtype=3).count(),
            f4 = StateChange.objects.filter(
                block=block,statechangetype="f",statechangesubtype=4).count(),
            f5 = StateChange.objects.filter(
                block=block,statechangetype="f",statechangesubtype=5).count(),
            f6 = StateChange.objects.filter(
                block=block,statechangetype="f",statechangesubtype=6).count(),
            f7 = StateChange.objects.filter(
                block=block,statechangetype="f",statechangesubtype=7).count(),
            f8 = StateChange.objects.filter(
                block=block,statechangetype="f",statechangesubtype=8).count(),
            f9 = StateChange.objects.filter(
                block=block,statechangetype="f",statechangesubtype=9).count(),
            f10 = StateChange.objects.filter(
                block=block,statechangetype="f",statechangesubtype=10).count(),
            f11 = StateChange.objects.filter(
                block=block,statechangetype="f",statechangesubtype=11).count(),
            f12 = StateChange.objects.filter(
                block=block,statechangetype="f",statechangesubtype=12).count(),
            f13 = StateChange.objects.filter(
                block=block,statechangetype="f",statechangesubtype=13).count(),
            wirings = StateChange.objects.filter(
                block=block,statechangetype="w").count(),
            sum = StateChange.objects.filter(
                block=block).count(),
        ))
    return statechangestatistics


# Create your views here.
def transaction_list(request):
    # Get a list with all statechanges with the highest blocknumer first
    statechangesbatches_list = Block.objects.order_by(
        "blocknumber").reverse()
    # Paginate the list https://docs.djangoproject.com/en/3.0/topics/pagination/
    statechange_paginator = Paginator(statechangesbatches_list,20)

    page = request.GET.get('page')
    if page == None:
        page = 1
    blocks = statechange_paginator.get_page(page)
    statechangestatistics = get_statechangestatistics(blocks)

    pagenrs = get_paginationnrs(
        page,
        statechange_paginator.num_pages
    )

    # Create graphs
    monthgraphinfo = get_monthgraphinfo()
    daygraphinfo = get_daygraphinfo()
    quartergraphinfo = get_quartergraphinfo()
    wiringgraphinfo = get_wiringgraphinfo()
    statechangetypeslast30day = get_statechangetypeslast30days()
    burngraphinfo = get_burngraphinfo()

    # Get Burnback info:
    # GET price
    geteurprice = CryptoPrice.objects.filter(name="GET")[0].price_eur
    # Amount of change changes:
    statechangesbuyback = quartergraphinfo[-1].value
    # Burn back value (statechanges x 0.07)
    burnbackvalue = statechangesbuyback * 0.07
    # GET burned:
    getburned = burnbackvalue / geteurprice
    # Open market burned:
    openmarketgetburned = getburned / 100 * 58

    #Roundup the numbers(afterward, to prevent wrong calculations):
    burnbackvalue = "{0:.2f}".format(burnbackvalue)
    getburned = "{0:.0f}".format(getburned)
    openmarketgetburned = "{0:.0f}".format(openmarketgetburned)


    return render(request,'statechanges/statechanges.html',{
        'statechangestatistics':statechangestatistics,
        'blocks':blocks,
        'pagenrs':pagenrs,
        'monthgraphinfo':monthgraphinfo,
        'daygraphinfo':daygraphinfo,
        'quartergraphinfo':quartergraphinfo,
        'wiringgraphinfo':wiringgraphinfo,
        'burngraphinfo':burngraphinfo,
        'statechangetypeslast30day':statechangetypeslast30day,
        'geteurprice':geteurprice,
        'burnbackvalue': burnbackvalue,
        'getburned': getburned,
        'openmarketgetburned':openmarketgetburned
        })
