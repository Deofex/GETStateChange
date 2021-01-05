from django.db.models import Sum
from datetime import datetime,timedelta
from .models import Block,Event
from .graphinfo_shared import GraphInfo

from .graphinfo_shared import GraphInfo, DoubleGraphInfo, get_monthtimerange

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
        sumwirings = (Block.objects.filter(
            date__range=[startdate,enddate]).values("wsum").aggregate(
            Sum("wsum"))).popitem()[1]

        # Create the label from the date in the following format day-month-year
        label = startdate.strftime("%d-%m-%Y")

        # Add the period to the graphinfo
        graphinfo.append(GraphInfo(
            label,
            sumwirings
        ))

        # Go back in time 1 day for the next run
        startdate = startdate - timedelta(days=1)
        enddate = enddate - timedelta(days=1)

    # Reverse the list created to get the oldest date on top
    graphinfo.reverse()

    # Return the list with the graph info
    return graphinfo

def get_eventsized30days():
    today = datetime.now()
    thirtydaysago = today - timedelta(days=30)
    events = Event.objects.filter(lastupdate__gt = thirtydaysago).exclude(
        hash = 'TheUnknownStateChangesParadise')
    zf = events.filter(totalsum__range=[1,49]).count()
    fh = events.filter(totalsum__range=[50,99]).count()
    htf = events.filter(totalsum__range=[100,249]).count()
    tft = events.filter(totalsum__range=[250,999]).count()
    tp = events.filter(totalsum__gt=1000).count()
    graphinfo = [
        GraphInfo('1-50', zf),
        GraphInfo('50-100',fh),
        GraphInfo('100-250',htf),
        GraphInfo('250,1000',tft),
        GraphInfo('1000 plus',tp),
    ]
    return graphinfo

# This function creates the info for the monthly statechanges graph
def get_monthgraphticketssoldinfo():
    # Get the last 12 time ranges
    timeranges = get_monthtimerange()
    # Create an empty list to store the graph info in
    graphinfo = []
    # Foreach timerange retrieve the amount of statechanges and translate the
    # month number and save both in the created list and return this object.
    for timerange in timeranges:
        # Get all statechanges in the timerange
        sumstatechanges = Block.objects.filter(
            date__range=[timerange.startdate,timerange.enddate]).aggregate(Sum(
                'f2sum'))['f2sum__sum']

        # Create the label from the date in the following format day-month-year
        label = timerange.startdate.strftime("%m-%Y")

        # Add the sum of the state changes and period name in an object and add
        # this to the list
        if sumstatechanges != None:
            graphinfo.append(GraphInfo(
                label,
                sumstatechanges
            ))

    # Return the list with the graph info
    return graphinfo