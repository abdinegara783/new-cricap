from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'), 
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('news/', views.news_view, name='news'),
    path('survey/', views.survey_views, name='survey'),
    path('dashboard-home/', views.dashboard_home_view, name='dashboard-home'),
    path('report/', views.report_views, name='report'),
    path('map/', views.map_views, name='map'),
    path('survey/survey_1/', views.survey_1_views, name='survey_1'),
    path('survey/survey_2/', views.survey_2_views, name='survey_2'),
    path('survey/survey_3/', views.survey_3_views, name='survey_3'),
    path('survey/survey_4/', views.survey_4_views, name='survey_4'),
    path('survey/survey_5/', views.survey_5_views, name='survey_5'),
    path('rata-rata/', views.calculate_average_response, name='rata-rata'),
]