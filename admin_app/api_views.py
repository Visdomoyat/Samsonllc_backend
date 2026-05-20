import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods

from .models import Product


def _json_error(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({'error': message}, status=status)


def _serialize_product(request, product: Product) -> dict:
    image_url = None
    if product.image:
        image_url = request.build_absolute_uri(product.image.url)
    return {
        'id': product.pk,
        'name': product.name,
        'description': product.description,
        'price': str(product.price),
        'image_url': image_url,
        'created_at': product.created_at.isoformat(),
        'updated_at': product.updated_at.isoformat(),
    }


@require_GET
def health(request):
    return JsonResponse({
        'status': 'ok',
        'service': 'Samsonllc API',
    })


@require_GET
@ensure_csrf_cookie
def session(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'authenticated': False})
    return JsonResponse({
        'authenticated': True,
        'user': {
            'id': user.pk,
            'username': user.username,
        },
    })


@require_http_methods(['POST'])
def login_view(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return _json_error('Invalid JSON body')

    username = (payload.get('username') or '').strip()
    password = payload.get('password') or ''
    if not username or not password:
        return _json_error('Username and password are required')

    user = authenticate(request, username=username, password=password)
    if user is None:
        return _json_error('Invalid credentials', status=401)

    login(request, user)
    return JsonResponse({
        'authenticated': True,
        'user': {
            'id': user.pk,
            'username': user.username,
        },
    })


@require_http_methods(['POST'])
@login_required
def logout_view(request):
    logout(request)
    return JsonResponse({'authenticated': False})


@require_GET
def product_list(request):
    products = Product.objects.all()
    return JsonResponse({
        'products': [_serialize_product(request, product) for product in products],
    })
