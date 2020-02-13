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