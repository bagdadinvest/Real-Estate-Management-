from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.index , name='index'),
    path('about/', views.about , name='about'),
    path('financing/', views.financing , name='financing'),
]
