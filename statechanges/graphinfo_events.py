from django.db.models import Sum
from datetime import datetime,timedelta
from .models import Block
from .graphinfo_shared import GraphInfo

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
        if sumwirings == None:
            sumwirings = 0
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