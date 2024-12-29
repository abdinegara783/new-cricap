from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
import requests
from .forms import RegistrationForm
from .forms import DataDiriForm
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from .models import Question, Response, Section, SubQuestion, Response, DataDiri, IRKResult
from django.contrib.auth.models import User
import folium
import pandas as pd
import geopandas as gpd
import numpy as np
# Create your views here.


def news_view(request):
    url = 'https://newsapi.org/v2/everything?q=keuangan&apiKey=e5cac2437c82460babf1d584b37eb92c'
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
    url = 'https://newsapi.org/v2/everything?q=keuangan&apiKey=e5cac2437c82460babf1d584b37eb92c'
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
    irk = IRKResult.objects.get(user=request.user)
    user = request.user.username  # Ambil username pengguna login
    username = DataDiri.objects.get(user=request.user) 
    context = {
        'username': username,
        'user': user,
        'irk': irk,
    }
    return render(request, 'dashboard_home.html', context)

def map_views(request):
    template = loader.get_template('map_view.html')
    return HttpResponse(template.render())

def report_views(request):
    # Create a map centered on Indonesia
    user = request.user.username
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
    context = {
        'user': user,
    }

    return render(request, 'report.html', context )
def survey_views(request):
    user = request.user.username
    context = {
        'user': user,
    }
    return render(request, 'survey.html', context )

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

# Define categories
def determine_category(value):
    if 1 <= value < 1.5 :
        return "Sangat Rendah"
    elif 1.51 <= value < 2.50:
        return "Rendah"
    elif 2.51 <= value < 3.50:
        return "Sedang"
    elif 3.51 <= value < 4.50:
        return "Tinggi"
    elif 4.51 <= value <= 5.00:
        return "Sangat Tinggi"
    else:
        return "Nilai tidak valid"


def calculate_average_response(request):
    user = request.user  # Ambil user yang sedang login
    responses = Response.objects.filter(user=user)  # Ambil semua jawaban user
    username = DataDiri.objects.get(user=request.user)

    # Konversi respons ke angka
    response_mapping = {
        'SS': 1,
        'S': 2,
        'R': 3,
        'TS': 4,
        'STS': 5
    }
    scores = np.array([response_mapping[response.response] for response in responses])  # Gunakan NumPy array

    # Operasi dengan NumPy
    if scores.size > 0:
        # Fase 1: Hitung rata-rata per kelompok
        x_1 = np.mean(scores[0:4])
        x_2 = np.mean(scores[4:8])
        x_3 = np.mean(scores[8:12])
        x_4 = np.mean(scores[12:16])
        x_5 = np.mean(scores[16:19])
        x_6 = np.mean(scores[19:22])
        x_7 = np.mean(scores[22:25])
        x_8 = np.mean(scores[25:28])
        x_9 = np.mean(scores[28:31])
        x_10 = np.mean(scores[31:34])
        x_11 = np.mean(scores[34:37])
        x_12 = np.mean(scores[37:40])
        x_13 = np.mean(scores[40:43])
        x_14 = np.mean(scores[43:46])
        x_15 = np.mean(scores[46:49])
        x_16 = np.mean(scores[49:52])
        # Fase 2: Hitung rata-rata gabungan sesuai kelompok
        y_1 = np.mean([x_1, x_2])
        y_2 = np.mean([x_3, x_4])
        y_3 = np.mean([x_5, x_6])
        y_4 = np.mean([x_7, x_8])
        y_5 = np.mean([x_9, x_10, x_11])
        y_6 = np.mean([x_12, x_13])
        y_7 = np.mean([x_14, x_15, x_16])
        # Calculate IRK
        irk = (0.8532 * y_1 + 0.2835 * y_2 + 0.3654 * y_3 +
            0.2897 * y_4 + 0.4650 * y_5 + 0.4524 * y_6 + 0.7192 * y_7)

    else:
        irk = 0
    category = determine_category(irk)

    # Simpan IRK dan kategori ke database
    irk_result, created = IRKResult.objects.get_or_create(user=user)
    irk_result.irk = irk
    irk_result.category = category
    irk_result.save()

    # Kirim hasil ke template
    context = {
        'username': username,
        'user': user,
        'irk': irk,
        'category': category,
    }
    return render(request, 'rata-rata.html', context)
# [4,4],[4,4],[3,3],[3,3],[3,3,3],[3,3],[3,3,3]




