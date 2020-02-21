from django.conf import settings
from django.core.management.base import BaseCommand
from statechanges.models import Block, Ticket, StateChange, Event, AppStatus


class Command(BaseCommand):
    '''Unlock import ready state in the database'''

    def handle(self, *args, **kwargs):
        importstatechangesready = AppStatus.objects.get(
            name="ImportStateChangesReady")
        importstatechangesready.enablestatus()