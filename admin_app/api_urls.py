from django.urls import path

from . import api_views

urlpatterns = [
    path('health/', api_views.health, name='api_health'),
    path('config/payments/', api_views.payment_config, name='api_payment_config'),
    path('auth/session/', api_views.session, name='api_session'),
    path('auth/login/', api_views.login_view, name='api_login'),
    path('auth/logout/', api_views.logout_view, name='api_logout'),
    path('products/', api_views.product_list, name='api_product_list'),
    path('contact/', api_views.contact_submit, name='api_contact_submit'),
    path('orders/', api_views.order_create, name='api_order_create'),
    path('orders/<int:pk>/', api_views.order_detail, name='api_order_detail'),
    path('orders/<int:pk>/pay/stripe/', api_views.order_pay_stripe, name='api_order_pay_stripe'),
    path(
        'orders/<int:pk>/pay/stripe/release/',
        api_views.order_release_stripe,
        name='api_order_release_stripe',
    ),
    path(
        'orders/<int:pk>/pay/paypal/release/',
        api_views.order_release_paypal,
        name='api_order_release_paypal',
    ),
    path('orders/<int:pk>/pay/paypal/', api_views.order_pay_paypal, name='api_order_pay_paypal'),
    path(
        'orders/<int:pk>/paypal/capture/',
        api_views.order_paypal_capture,
        name='api_order_paypal_capture',
    ),
    path('webhooks/stripe/', api_views.stripe_webhook, name='api_stripe_webhook'),
    path('webhooks/paypal/', api_views.paypal_webhook, name='api_paypal_webhook'),
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
