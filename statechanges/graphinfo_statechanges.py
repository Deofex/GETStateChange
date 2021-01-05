from django.db.models import Sum
from django.utils.translation import gettext as _
from datetime import datetime, timedelta
from .models import Block, StateChange
from .graphinfo_shared import GraphInfo, DoubleGraphInfo, get_monthtimerange, \
get_quartertimerange

# Create statechange batch info object which can be used in the template
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

# Function to create the amount of buttons shown under the blocks graph
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
        sumstatechanges = Block.objects.filter(
            date__range=[timerange.startdate,timerange.enddate]).values(
                'statechange').count()

        # Create the label from the date in the following format day-month-year
        label = timerange.startdate.strftime("%m-%Y")

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
        sumstatechanges = Block.objects.filter(
            date__range=[timerange.startdate,timerange.enddate]).values(
                'statechange').count()

        # Create the label from the date in the following format day-month-year
        label = timerange.startdate.strftime("%m-%Y")

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
        sumstatechanges = Block.objects.filter(
            date__range=[startdate,enddate]).aggregate(Sum(
                'totalsum'))['totalsum__sum']

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
    statechangesbatchesinrange = Block.objects.filter(
        date__range=[startdate,enddate])
    # Create an empty array
    graphinfo = []
    # Cycle through 0 to 13 (amount of state changes)
    for i in range(0,14):
        # Get the amount of state changes of the type firings + i
        sum = 'f' + str(i) + 'sum'
        statechangefirings = (statechangesbatchesinrange.values(sum).aggregate(
            Sum(sum))).popitem()[1]

        # Get the label of the firing
        nameconvert = {
            0: _("Tickets created"),
            1: _("Tickets blocked"),
            2: _("Tickets sold in the primary market"),
            3: _("Tickets sold in secondary market"),
            4: _("Tickets bought back"),
            5: _("Tickets cancelled"),
            6: _("Ticket put for sale"),
            7: _("No Show"),
            8: _("Not resold"),
            9: _("Not sold in primary market"),
            10: _("Not sold in secondary market"),
            11: _("Tickets scanned"),
            12: _("Show over"),
            13: _("Tickets unblocked")
        }
        label = nameconvert.get(i, _("Unknown"))

        # If more than 0 statechanges of the specific type occured, add it to
        # the array
        if statechangefirings != 0:
            graphinfo.append(GraphInfo(
                label,
                statechangefirings
            ))
    # Return the array
    return graphinfo
