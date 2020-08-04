from django.conf import settings
from django.core.management.base import BaseCommand
from statechanges.models import Ticket


class Command(BaseCommand):
    '''Reset all update times for the tickets'''

    def handle(self, *args, **kwargs):
        tickets = Ticket.objects.all()
        ticketcount = tickets.count()
        counter = 0
        for ticket in tickets:
            counter += 1
            print("Update ticket: {} of {}".format(counter,ticketcount))
            d = ticket.statechange_set.all().order_by('block').last().block.date
            ticket.lastupdate = d
            ticket.save()
