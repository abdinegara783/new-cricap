from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
import requests
from .forms import RegistrationForm
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from .models import Question, Response, Section, SubQuestion
import folium
import pandas as pd
import geopandas as gpd
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

def survey_view(request):
    section = Section.objects.all()
    main_question = Question.objects.all()
    sub_questions = SubQuestion.objects.all()

    if request.method == 'POST':
        # Loop melalui setiap pertanyaan untuk menyimpan respons
        for sub_question in sub_questions:
            response_value = request.POST.get(f'question_{sub_question.id}')
            if response_value:
                Response.objects.create(
                    user=request.user,
                    sub_question=sub_question,
                    response=response_value
                )
        return redirect('home')
    
    
    context = {
        'section': section,
        'main_question': main_question,
        'sub_questions' : sub_questions
    }
    
    return render(request, 'survey.html', context)

def dashboard_home_view(request):
    template = loader.get_template('dashboard_home.html')
    return HttpResponse(template.render())
def map_views(request):
    template = loader.get_template('map_view.html')
    return HttpResponse(template.render())

def report_views(request):
    # Create a map centered on Indonesia
    m = folium.Map(location=[-2.5489, 118.0149], zoom_start=5)

    # Load Indonesia GeoJSON data (you'll need to provide this file)
    indonesia_geojson = gpd.read_file('geopackage\indonesia.geojson')

    # Sample data for cities (replace with your actual data)
    data = {
        'city': ['Jakarta', 'Surabaya', 'Medan', 'Bandung', 'Makassar'],
        'lat': [-6.2088, -7.2575, 3.5952, -6.9175, -5.1477],
        'lon': [106.8456, 112.7521, 98.6722, 107.6191, 119.4327],
        'status': ['High', 'Medium', 'Low', 'Medium', 'High']
    }
    df = pd.DataFrame(data)

    # Add choropleth layer
    folium.Choropleth(
        geo_data=indonesia_geojson,
        name='Indonesia',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
    ).add_to(m)

    # Add markers for cities
    for idx, row in df.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=10,
            popup=f"{row['city']}: {row['status']}",
            color='blue' if row['status'] == 'Low' else 'orange' if row['status'] == 'Medium' else 'red',
            fill=True,
            fill_color='blue' if row['status'] == 'Low' else 'orange' if row['status'] == 'Medium' else 'red'
        ).add_to(m)

    # Save the map to an HTML file
    m.save('mystaticfiles/map/map.html')

    return render(request, 'report.html')


