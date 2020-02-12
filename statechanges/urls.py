from django.urls import path
from . import views

urlpatterns = [
    path('',
        views.page_home,
        name='page_home'
    ),
    path('statechanges',
        views.page_statechanges,
        name='page_statechanges',
    ),
    path('events',
        views.page_events,
        name='page_events'
    ),
    path('events/<str:eventhash>',
        views.page_singleevent,
        name='page_singleevent'
    )
]
