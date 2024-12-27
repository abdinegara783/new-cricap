from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
import requests
from .forms import RegistrationForm
from .forms import DataDiriForm
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from .models import Question, Response, Section, SubQuestion, Response, DataDiri
from django.contrib.auth.models import User
import folium
import pandas as pd
import geopandas as gpd
import numpy as np
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
            return redirect('dashboard-home')
    else:
        form = AuthenticationForm()
    return render(request, 'login_view.html', {'form': form})

def dashboard_home_view(request):
    username = request.user.username  # Ambil username pengguna login
    return render(request, 'dashboard_home.html', {'username': username})

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
def survey_views(request):
    template = loader.get_template('survey.html')
    return HttpResponse(template.render())

def survey_1_views(request):
    template = loader.get_template('survey_1.html')
    return HttpResponse(template.render())
def survey_2_views(request):
    template = loader.get_template('survey_2.html')
    return HttpResponse(template.render())


def survey_3_views(request):
    user = request.user  # Ambil pengguna yang sedang login
    try:
        # Coba ambil data diri pengguna jika sudah ada
        data_diri = DataDiri.objects.get(user=user)
    except DataDiri.DoesNotExist:
        # Jika data tidak ada, buat objek baru (tetap, user akan diisi secara otomatis)
        data_diri = None

    if request.method == "POST":
        form = DataDiriForm(request.POST, instance=data_diri)  # Isi form dengan data yang ada (jika ada)
        if form.is_valid():
            data_diri = form.save(commit=False)  # Jangan simpan dulu
            data_diri.user = user  # Tentukan user yang sedang login
            data_diri.save()  # Simpan ke database
            return redirect('survey_4')  # Ganti 'survey_4' dengan nama URL selanjutnya
    else:
        form = DataDiriForm(instance=data_diri)  # Isi form dengan data yang ada (jika ada)

    return render(request, 'survey_3.html', {'form': form})


def survey_4_views(request):
    section = Section.objects.all()
    main_question = Question.objects.all()
    sub_questions = SubQuestion.objects.all()
    username = request.user.username

    if request.method == 'POST':
        # Loop melalui setiap pertanyaan untuk menyimpan atau memperbarui respons
        for sub_question in sub_questions:
            response_value = request.POST.get(f'question_{sub_question.id}')
            if response_value:
                # Cari apakah respons untuk user dan sub_question sudah ada
                response, created = Response.objects.get_or_create(
                    user=request.user,
                    sub_question=sub_question,
                    defaults={'response': response_value}
                )
                if not created:  # Jika sudah ada, perbarui respons
                    response.response = response_value
                    response.save()

        return redirect('survey_5')

    context = {
        'section': section,
        'main_question': main_question,
        'sub_questions': sub_questions,
        'username': username
    }
    
    return render(request, 'survey_4.html', context)

def survey_5_views(request):
    template = loader.get_template('survey_5.html')
    return HttpResponse(template.render())


def calculate_average_response(request):
    user = request.user  # Ambil user yang sedang login
    responses = Response.objects.filter(user=user)  # Ambil semua jawaban user

    # Konversi respons ke angka
    response_mapping = {
        'SS': 1,
        'S': 2,
        'R': 3,
        'TS': 4,
        'STS': 5
    }
    scores = np.array([response_mapping[response.response] for response in responses])  # Gunakan NumPy array

    # Debug: Print array scores
    print(f"Scores array: {scores}")  # Akan muncul di terminal server

    # Operasi dengan NumPy
    if scores.size > 0:
        average_score = np.mean(scores)  # Hitung rata-rata menggunakan NumPy
        max_score = np.max(scores)      # Nilai maksimum
        min_score = np.min(scores)      # Nilai minimum
        std_dev = np.std(scores)        # Standar deviasi
    else:
        average_score = None  # Jika tidak ada respons
        max_score = None
        min_score = None
        std_dev = None

    # Kirim hasil ke template
    context = {
        'scores': scores,              # Bisa dikirim ke template jika perlu
        'average_score': average_score,
        'max_score': max_score,
        'min_score': min_score,
        'std_dev': std_dev,
    }
    return render(request, 'rata-rata.html', context)




