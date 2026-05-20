from django.urls import path

from . import api_views

urlpatterns = [
    path('health/', api_views.health, name='api_health'),
    path('auth/session/', api_views.session, name='api_session'),
    path('auth/login/', api_views.login_view, name='api_login'),
    path('auth/logout/', api_views.logout_view, name='api_logout'),
    path('products/', api_views.product_list, name='api_product_list'),
]
