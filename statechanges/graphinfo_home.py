from .graphinfo_shared import GraphInfo, TimeRange
from .models import Block
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
