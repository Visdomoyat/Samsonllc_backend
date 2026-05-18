from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def landing(request):
    return render(request, 'landing.html')


@login_required
def search(request):
    query = request.GET.get('q', '').strip()
    return render(request, 'landing.html', {'search_query': query})


@login_required
def shop(request):
    return render(request, 'landing.html')


@login_required
def purchased(request):
    return render(request, 'landing.html')


@login_required
def transactions(request):
    return render(request, 'landing.html')
