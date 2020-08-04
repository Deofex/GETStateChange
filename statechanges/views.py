from django.shortcuts import render
from .models import Block, Event
from .models import CryptoPrice
from django.core.paginator import Paginator
from .graphinfo_statechanges import get_monthgraphinfo,get_daygraphinfo,\
    get_quartergraphinfo,get_statechangetypeslast30days,get_paginationnrs
from .graphinfo_home import get_buybackgraphinfo,\
    get_statechangesfiringlast24h,get_eventsactivelast24h,get_burngraphinfo
from .graphinfo_events import get_wiringgraphinfo, get_eventsized30days

# Create your views here.
def page_statechanges(request):
    # Get a list with all statechanges with the highest blocknumer first
    statechangesbatches_list = Block.objects.order_by(
        "blocknumber").reverse()
    # Paginate the list https://docs.djangoproject.com/en/3.0/topics/pagination/
    statechange_paginator = Paginator(statechangesbatches_list,10)

    page = request.GET.get('page')
    if page == None:
        page = 1
    pageblocks = statechange_paginator.get_page(page)

    pagenrs = get_paginationnrs(
        page,
        statechange_paginator.num_pages
    )

    # Create graphs
    monthgraphinfo = get_monthgraphinfo()
    daygraphinfo = get_daygraphinfo()
    quartergraphinfo = get_quartergraphinfo()
    statechangetypeslast30day = get_statechangetypeslast30days()

    # Get Burnback info:
    # GET price
    geteurprice = CryptoPrice.objects.filter(name="GET")[0].price_eur
    # Amount of change changes:
    statechangesbuyback = quartergraphinfo[-1].value
    # Burn back value (statechanges x 0.07)
    burnbackvalue = statechangesbuyback * 0.07
    # GET burned:
    getburned = burnbackvalue / geteurprice
    # Open market burned:
    openmarketgetburned = getburned / 100 * 58

    #Roundup the numbers(afterward, to prevent wrong calculations):
    burnbackvalue = "{0:.2f}".format(burnbackvalue)
    getburned = "{0:.0f}".format(getburned)
    openmarketgetburned = "{0:.0f}".format(openmarketgetburned)


    return render(request,'statechanges/statechanges.html',{
        'pageblocks':pageblocks,
        'pagenrs':pagenrs,
        'monthgraphinfo':monthgraphinfo,
        'daygraphinfo':daygraphinfo,
        'quartergraphinfo':quartergraphinfo,
        'statechangetypeslast30day':statechangetypeslast30day,
        'burnbackvalue': burnbackvalue,
        'navbar':'page_statechanges'
        })


# Create your views here.
def page_home(request):
    # Get buyback graph info
    buybackinfo = get_buybackgraphinfo()

    # Get the amount of tickets sold last 24 hours on the primaire and
    # secondairy markets
    ticketssoldlast24h = get_statechangesfiringlast24h(2) + \
        get_statechangesfiringlast24h(3)

    # Get the amount of tickets scanned in the last 24 hours
    ticketsscannedlast24h = get_statechangesfiringlast24h(11)

    # Events active last 24 hours
    eventsactivelast24h = get_eventsactivelast24h()
    # Get Burnback info:
    # GET price
    geteurprice = CryptoPrice.objects.filter(name="GET")[0].price_eur
    # Amount of change changes:
    statechangesbuyback = (float(buybackinfo[-1].value) / 0.07)
    # Burn back value (statechanges x 0.07)
    burnbackvalue = statechangesbuyback * 0.07
    # GET burned:
    getburned = burnbackvalue / geteurprice
    # Open market burned:
    openmarketgetburned = getburned / 100 * 58

    # Get burn info
    burngraphinfo = get_burngraphinfo()
    #Roundup the numbers(afterward, to prevent wrong calculations):
    burnbackvalue = "{0:.0f}".format(burnbackvalue)
    getburned = "{0:.0f}".format(getburned)
    openmarketgetburned = "{0:.0f}".format(openmarketgetburned)


    return render(request,'statechanges/home.html',{
        'buybackinfo':buybackinfo,
        'ticketssoldlast24h':ticketssoldlast24h,
        'ticketsscannedlast24h':ticketsscannedlast24h,
        'eventsactivelast24h':eventsactivelast24h,
        'geteurprice':"{:.2f}".format(geteurprice),
        'burnbackvalue': burnbackvalue,
        'getburned': getburned,
        'openmarketgetburned':openmarketgetburned,
        'burngraphinfo':burngraphinfo,
        'navbar':'page_home'
    })

# Page view for a single event
def page_events(request):
    # Get a list with all Events sorted on the latest updates
    event_list = Event.objects.exclude(totalsum = 0).exclude(
        hash = 'TheUnknownStateChangesParadise').order_by(
        "lastupdate").reverse()
    # Paginate the list https://docs.djangoproject.com/en/3.0/topics/pagination/
    event_paginator = Paginator(event_list,10)

    # Get page numbers
    page = request.GET.get('page')
    if page == None:
        page = 1
    pageevents = event_paginator.get_page(page)

    pagenrs = get_paginationnrs(
        page,
        event_paginator.num_pages
    )

    # Get information for the new event chart
    wiringgraphinfo = get_wiringgraphinfo()
    return render(request,'statechanges/events.html',{
        'pageevents':pageevents,
        'pagenrs':pagenrs,
        'wiringgraphinfo':wiringgraphinfo,
        'eventsized30days':get_eventsized30days,
        'navbar':'page_events',
    })

# Page for a single event
def page_singleevent(request,eventhash):
    # Get all events
    event = Event.objects.get(hash=eventhash)
    # Get a list with all tickets
    ticket_list = event.ticket_set.order_by('-lastupdate')
    # Count the amount of tickets corresponding to the event
    ticketcount = ticket_list.count()
    # Paginate the list https://docs.djangoproject.com/en/3.0/topics/pagination/
    ticket_paginator = Paginator(ticket_list,10)

    page = request.GET.get('page')
    if page == None:
        page = 1
    pagetickets = ticket_paginator.get_page(page)

    pagenrs = get_paginationnrs(
        page,
        ticket_paginator.num_pages
    )

    return render(request,'statechanges/singleevent.html',{
        'event':event,
        'ticketcount':ticketcount,
        'pagetickets':pagetickets,
        'pagenrs':pagenrs,
    })

# Page for a single block
def page_singleblock(request,blocknumber):
    # Get the information from the block
    singleblock = Block.objects.get(blocknumber=blocknumber)
    # Get a list with all statechanges in the block
    statechange_list = singleblock.statechange_set.all()
    # Paginate the list https://docs.djangoproject.com/en/3.0/topics/pagination/
    statechange_paginator = Paginator(statechange_list,10)

    page = request.GET.get('page')
    if page == None:
        page = 1
    pagestatechanges = statechange_paginator.get_page(page)

    pagenrs = get_paginationnrs(
        page,
        statechange_paginator.num_pages
    )

    return render(request,'statechanges/singleblock.html',{
        'singleblock':singleblock,
        'pagestatechanges':pagestatechanges,
        'pagenrs':pagenrs,
    })