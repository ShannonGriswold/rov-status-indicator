from django.urls import path

from . import views

app_name = 'web_indicator'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]
