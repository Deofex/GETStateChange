from datetime import datetime, timedelta

# create a graph class where to store periods and a single value
class GraphInfo():
    def __init__(self,periodname,value):
        self.periodname = periodname
        self.value = value

# Create a graph which can store periods and store two values
class DoubleGraphInfo(GraphInfo):
    def __init__(self, periodname, value, secondvalue):
        super().__init__(periodname, value)
        self.secondvalue = secondvalue

# Create a class which can store 2 timeranges
class TimeRange():
    def __init__(self,startdate,enddate):
        self.startdate = startdate
        self.enddate = enddate

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
