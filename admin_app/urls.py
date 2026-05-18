from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('search/', views.search, name='search'),
    path('shop/', views.shop, name='shop'),
    path('purchased/', views.purchased, name='purchased'),
    path('transactions/', views.transactions, name='transactions'),
    path('logout/', LogoutView.as_view(next_page='landing'), name='logout'),
]
