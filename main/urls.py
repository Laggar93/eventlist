from django.urls import path
from . import views

urlpatterns = [
    path('add-event/', views.add_event_to_calendar, name='add_event'),
    path('', views.main_page_view),
]