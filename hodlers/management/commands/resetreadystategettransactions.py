from django.conf import settings
from django.core.management.base import BaseCommand
from hodlers.models import TAppStatus


class Command(BaseCommand):
    '''Unlock import ready state in the database'''

    def handle(self, *args, **kwargs):
        importstatechangesready = TAppStatus.objects.get(
            name="ImportGETTransactionsReady")
        importstatechangesready.enablestatus()