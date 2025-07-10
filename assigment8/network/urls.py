from django.urls import path
from . import views

urlpatterns = [
    path('', views.network_view, name='network_form'),
    path('leases/', views.lease_list_view, name='lease_list'),
]