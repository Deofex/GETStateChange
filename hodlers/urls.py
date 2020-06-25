from django.urls import path
from . import views

urlpatterns = [
    path('',
        views.page_hodlers,
        name='page_hodlers'
    ),
]
