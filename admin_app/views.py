from django.shortcuts import render


def landing(request):
    return render(request, 'landing.html')


def search(request):
    query = request.GET.get('q', '').strip()
    return render(request, 'landing.html', {'search_query': query})


def shop(request):
    return render(request, 'landing.html')


def purchased(request):
    return render(request, 'landing.html')


def transactions(request):
    return render(request, 'landing.html')
