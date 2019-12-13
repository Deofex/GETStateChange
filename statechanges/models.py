from django.db import models
from django.utils import timezone

# Create your models here.
class StateChange(models.Model):
    '''Summery of GET state changes which are posted hourly on the blockchain'''
    date = models.DateTimeField()
    blocknumber = models.IntegerField()
    sumstatechanges = models.IntegerField()
    firings0count = models.IntegerField()
    firings1count = models.IntegerField()
    firings2count = models.IntegerField()
    firings3count = models.IntegerField()
    firings4count = models.IntegerField()
    firings5count = models.IntegerField()
    firings6count = models.IntegerField()
    firings7count = models.IntegerField()
    firings8count = models.IntegerField()
    firings9count = models.IntegerField()
    firings10count = models.IntegerField()
    firings11count = models.IntegerField()
    firings12count = models.IntegerField()
    firings13count = models.IntegerField()
    wiringscount = models.IntegerField()
    unknownscount = models.IntegerField()


