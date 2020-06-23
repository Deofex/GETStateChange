from django.core.management.base import BaseCommand

class Command(BaseCommand):
    '''Unlock import ready state in the database'''

    def handle(self, *args, **kwargs):
        print("here's johnny")