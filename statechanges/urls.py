from django.urls import path
from . import views

urlpatterns = [
    path('',
    views.page_home,
    name='page_home'),
    path('statechanges',
    views.page_statechanges,
    name='page_statechanges'),
    path('eventstatistics',
    views.page_eventstatistics,
    name='page_eventstatistics'),
]
