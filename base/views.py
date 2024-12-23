from django.shortcuts import render
from django.http import HttpResponse
import requests
from .forms import RegistrationForm
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
# Create your views here.


def news_view(request):
    url = 'https://newsapi.org/v2/everything?q=finance&apiKey=e5cac2437c82460babf1d584b37eb92c'
    response = requests.get(url)
    data = response.json()

    # Mengambil 3 artikel teratas
    articles = data['articles']

    # Kirim data ke template
    context = {
        'articles': articles
    }
    return render(request, 'news.html', context)

def home(request):
    url = 'https://newsapi.org/v2/everything?q=finance&apiKey=e5cac2437c82460babf1d584b37eb92c'
    response = requests.get(url)
    data = response.json()

    # Mengambil 3 artikel teratas
    articles = data['articles'][:3]

    # Kirim data ke template
    context = {
        'articles': articles
    }
    return render(request, 'home.html', context)

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render (request, 'register_view.html', {'form':form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('survey')
    else:
        form = AuthenticationForm()
    return render(request, 'login_view.html', {'form': form})