from django.urls import path

from . import api_views

urlpatterns = [
    path('health/', api_views.health, name='api_health'),
    path('auth/session/', api_views.session, name='api_session'),
    path('auth/login/', api_views.login_view, name='api_login'),
    path('auth/logout/', api_views.logout_view, name='api_logout'),
    path('products/', api_views.product_list, name='api_product_list'),
    path('orders/', api_views.order_create, name='api_order_create'),
    path('admin/orders/', api_views.admin_order_list, name='api_admin_order_list'),
    path(
        'admin/orders/<int:pk>/',
        api_views.admin_order_detail,
        name='api_admin_order_detail',
    ),
    path(
        'admin/orders/<int:pk>/send-tracking/',
        api_views.admin_order_send_tracking,
        name='api_admin_order_send_tracking',
    ),
]
