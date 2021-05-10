from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('patent/<uuid:id>/', views.patent, name='patent'),
    url(r'^$', views.index, name='index')
]