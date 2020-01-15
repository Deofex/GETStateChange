from django.shortcuts import render
from .models import StateChange
from django.core.paginator import Paginator
from datetime import datetime
from datetime import timedelta

class TimeRange():
    def __init__(self,startdate,enddate):
        self.startdate = startdate
        self.enddate = enddate

class GraphInfo():
    def __init__(self,periodname,statechanges):
        self.periodname = periodname
        self.statechanges = statechanges

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
        # Get all statechanges batches in the timerange
        statechangebatches = StateChange.objects.filter(
            date__range=[timerange.startdate,timerange.enddate])

        # Loop through the batches and get the sum of all state changes
        sumstatechanges = 0
        for statechangebatch in statechangebatches:
            sumstatechanges += statechangebatch.sumstatechanges

        # Translate the month number of the timerange to a readable month
        if timerange.startdate.month == 1:
            periodname = 'Jan.'
        elif timerange.startdate.month == 2:
            periodname = 'Feb.'
        elif timerange.startdate.month == 3:
            periodname = 'Mar.'
        elif timerange.startdate.month == 4:
            periodname = 'Apr.'
        elif timerange.startdate.month == 5:
            periodname = 'May'
        elif timerange.startdate.month == 6:
            periodname = 'Jun.'
        elif timerange.startdate.month == 7:
            periodname = 'Jul.'
        elif timerange.startdate.month == 8:
            periodname = 'Aug.'
        elif timerange.startdate.month == 9:
            periodname = 'Sep.'
        elif timerange.startdate.month == 10:
            periodname = 'Oct.'
        elif timerange.startdate.month == 11:
            periodname = 'Nov.'
        elif timerange.startdate.month == 12:
            periodname = 'Dec.'

        # Add the sum of the state changes and period name in an object and add
        # this to the list
        if sumstatechanges != 0:
            graphinfo.append(GraphInfo(
                periodname,
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
        # Get all statechanges batches in the timerange
        statechangebatches = StateChange.objects.filter(
            date__range=[timerange.startdate,timerange.enddate])

        # Loop through the batches and get the sum of all state changes
        sumstatechanges = 0
        for statechangebatch in statechangebatches:
            sumstatechanges += statechangebatch.sumstatechanges

        # Translate the month number of the timerange to a readable quarter
        if timerange.startdate.month < 4:
            periodname = "Q1 " + str(timerange.startdate.year)
        elif timerange.startdate.month < 7:
            periodname = "Q2 " + str(timerange.startdate.year)
        elif timerange.startdate.month < 10:
            periodname = "Q3 " + str(timerange.startdate.year)
        else:
            periodname = "Q4 " + str(timerange.startdate.year)

        # Add the sum of the state changes and period name in an object and add
        # this to the list
        if sumstatechanges != 0:
            graphinfo.append(GraphInfo(
                periodname,
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
        statechangebatches = StateChange.objects.filter(
            date__range=[startdate,enddate])
        # Loop through the batches and get the sum of all state changes
        sumstatechanges = 0

        # Period name = a minus character + the number of days in the past being
        # processed
        periodname = str(startdate.day) + "-" + str(startdate.month)

        # Loop through each state changes and add the number of state changes to
        # the sumstatechanges variabele
        for statechangebatch in statechangebatches:
            sumstatechanges += statechangebatch.sumstatechanges

        # Add the period to the graphinfo
        graphinfo.append(GraphInfo(
            periodname,
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
        startdate = startdate - timedelta(days=1)
        enddate = enddate - timedelta(days=1)
        # Get all statechanges batches in the timerange
        statechangebatches = StateChange.objects.filter(
            date__range=[startdate,enddate])
        # Loop through the batches and get the sum of all state changes
        wiringstatechanges = 0

        # Period name = a minus character + the number of days in the past being
        # processed
        periodname = str(startdate.day) + "-" + str(startdate.month)

        # Loop through each state changes and add the number of wirings to
        # the wiring statechanges variabele
        for statechangebatch in statechangebatches:
            wiringstatechanges += statechangebatch.wiringscount

        # Add the period to the graphinfo
        graphinfo.append(GraphInfo(
            periodname,
            wiringstatechanges
        ))

    # Reverse the list created to get the oldest date on top
    graphinfo.reverse()

    # Return the list with the graph info
    return graphinfo




# Create your views here.
def transaction_list(request):
    # Get a list with all statechanges with the highest blocknumer first
    statechanges_list = StateChange.objects.order_by("blocknumber").reverse()
    # Paginate the list https://docs.djangoproject.com/en/3.0/topics/pagination/
    statechange_paginator = Paginator(statechanges_list,15)

    page = request.GET.get('page')
    if page == None:
        page = 1
    statechanges = statechange_paginator.get_page(page)

    pagenrs = get_paginationnrs(
        page,
        statechange_paginator.num_pages
    )

    monthgraphinfo = get_monthgraphinfo()
    daygraphinfo = get_daygraphinfo()
    quartergraphinfo = get_quartergraphinfo()
    wiringgraphinfo = get_wiringgraphinfo()

    return render(request,'statechanges/statechanges.html',{
        'statechanges':statechanges,
        'pagenrs':pagenrs,
        'monthgraphinfo':monthgraphinfo,
        'daygraphinfo':daygraphinfo,
        'quartergraphinfo':quartergraphinfo,
        'wiringgraphinfo':wiringgraphinfo
        })
