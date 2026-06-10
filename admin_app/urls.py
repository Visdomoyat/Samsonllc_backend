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
 
    path('logout/', LogoutView.as_view(), name='logout'),
    
    path('shop/', views.shop, name='shop'),
    path('shop/add/', views.product_create, name='product_create'),
    path('shop/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('shop/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('stacks-blends/', views.stack_blend_list, name='stack_blend_list'),
    path('stacks-blends/add/', views.stack_blend_create, name='stack_blend_create'),
    path(
        'stacks-blends/<int:pk>/edit/',
        views.stack_blend_edit,
        name='stack_blend_edit',
    ),
    path(
        'stacks-blends/<int:pk>/delete/',
        views.stack_blend_delete,
        name='stack_blend_delete',
    ),
    path('purchased/', views.purchased, name='purchased'),
    path('purchased/<int:pk>/update/', views.purchased_order_update, name='purchased_order_update'),
    path(
        'purchased/<int:pk>/send-tracking/',
        views.purchased_send_tracking,
        name='purchased_send_tracking',
    ),
    path(
        'purchased/<int:pk>/delete/',
        views.purchased_order_delete,
        name='purchased_order_delete',
    ),
    path('transactions/', views.transactions, name='transactions'),
    path('account/', views.account_settings, name='account_settings'),
]
