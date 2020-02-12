from django.db.models import Sum
from .graphinfo_shared import GraphInfo, TimeRange
from .models import Block,Event
from datetime import datetime
from datetime import timedelta

# This function creates the info for the buyback statechanges graph
def get_buybackgraphinfo():
    # Get the current day
    date = datetime.now()
    # Get the first date of the quarter
    if date.month < 4:
        startdate = datetime(date.year, 1, 1)
    elif date.month < 7:
        startdate = datetime(date.year, 4, 1)
    elif date.month < 10:
        startdate = datetime(date.year, 7, 1)
    else:
        startdate = datetime(date.year, 10, 1)

    # Set the initial end date 1 day after the start date
    enddate = startdate + timedelta(days=1)

    sumstatechanges = 0
    # Create an empty list
    graphinfo = []
    while True:
        # Get all statechanges batches in the timerange
        sumstatechanges = sumstatechanges + Block.objects.filter(
            date__range=[startdate,enddate]).values('statechange').count()

        # Create the label from the date in the following format day-month-year
        label = startdate.strftime("%d-%m-%Y")

        buybackvalue = "{0:.0f}".format(sumstatechanges * 0.07)
        # Add the label and statestatechange to the array
        graphinfo.append(GraphInfo(
            label,
            buybackvalue
        ))

        # Set the start and enddate 1 day later
        startdate = startdate + timedelta(days=1)
        enddate = enddate + timedelta(days=1)

        # If the start date is in the future, stop the loop
        if startdate > date:
            break

    # Return the list with the graph info
    return graphinfo

# Get the number of statechanges of a specific firing processed in the last
# 24 hours
def get_statechangesfiringlast24h(firingtype):
    # Enddate is now, start date is 1 day ago
    enddate = datetime.now()
    startdate = enddate - timedelta(days=1)

    # Query the amount of statechanges in the time
    sum = 'f' + str(firingtype) + 'sum'
    sumstatechanges = (Block.objects.filter(
        date__range=[startdate,enddate]).values(sum).aggregate(
            Sum(sum))).popitem()[1]

    # If there aren't statechanges in the last 24h set the amount on 0
    if sumstatechanges == None:
        sumstatechanges = 0

    # Return the amount of statechanges
    return sumstatechanges

# Function to get the number of events which were active in the last 24 hours
def get_eventsactivelast24h():
    # Enddate is now, start date is 1 day ago
    enddate = datetime.now()
    startdate = enddate - timedelta(days=1)

    # Query the amount of events active in the last 24 hours
    activeevents = Event.objects.filter(
        lastupdate__range=[startdate,enddate]).count()

    # Return the amount of events which were active alst 24 hours
    return activeevents
