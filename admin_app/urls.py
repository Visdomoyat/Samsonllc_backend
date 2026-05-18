from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .forms import LoginForm

urlpatterns = [
    path('', LoginView.as_view(
        template_name='login.html',
        authentication_form=LoginForm,
        redirect_authenticated_user=True,
    ), name='login'),
    path('home/', views.landing, name='landing'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('search/', views.search, name='search'),
    path('shop/', views.shop, name='shop'),
    path('purchased/', views.purchased, name='purchased'),
    path('transactions/', views.transactions, name='transactions'),
]
