from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'), 
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('news/', views.news_view, name='news'),
    path('survey/', views.survey_view, name='survey'),
    path('dashboard-home/', views.dashboard_home_view, name='dashboard-home'),
    path('report/', views.report_views, name='report'),
    path('map/', views.map_views, name='map'),
]