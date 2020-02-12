from django.shortcuts import render
from .models import Block, Event
from .models import CryptoPrice
from django.core.paginator import Paginator
from .graphinfo_statechanges import get_monthgraphinfo,get_daygraphinfo,\
    get_quartergraphinfo,get_statechangetypeslast30days,\
        get_burngraphinfo,get_paginationnrs
from .graphinfo_home import get_buybackgraphinfo,\
    get_statechangesfiringlast24h,get_eventsactivelast24h
from .graphinfo_events import get_wiringgraphinfo

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
    burngraphinfo = get_burngraphinfo()

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
        'burngraphinfo':burngraphinfo,
        'statechangetypeslast30day':statechangetypeslast30day,
        'geteurprice':geteurprice,
        'burnbackvalue': burnbackvalue,
        'getburned': getburned,
        'openmarketgetburned':openmarketgetburned,
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

    #Roundup the numbers(afterward, to prevent wrong calculations):
    burnbackvalue = "{0:.0f}".format(burnbackvalue)
    getburned = "{0:.0f}".format(getburned)
    openmarketgetburned = "{0:.0f}".format(openmarketgetburned)


    return render(request,'statechanges/home.html',{
        'buybackinfo':buybackinfo,
        'ticketssoldlast24h':ticketssoldlast24h,
        'ticketsscannedlast24h':ticketsscannedlast24h,
        'eventsactivelast24h':eventsactivelast24h,
        'geteurprice':geteurprice,
        'burnbackvalue': burnbackvalue,
        'getburned': getburned,
        'openmarketgetburned':openmarketgetburned,
        'navbar':'page_home'
    })

def page_events(request):
    # Get a list with all Events with the latest updates
    event_list = Event.objects.exclude(totalsum = 0).order_by(
        "totalsum").reverse()
    # Paginate the list https://docs.djangoproject.com/en/3.0/topics/pagination/
    event_paginator = Paginator(event_list,10)

    page = request.GET.get('page')
    if page == None:
        page = 1
    pageevents = event_paginator.get_page(page)

    pagenrs = get_paginationnrs(
        page,
        event_paginator.num_pages
    )

    wiringgraphinfo = get_wiringgraphinfo()
    return render(request,'statechanges/events.html',{
        'pageevents':pageevents,
        'pagenrs':pagenrs,
        'wiringgraphinfo':wiringgraphinfo,
        'navbar':'page_events'
    })