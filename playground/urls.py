from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('hello/', views.say_hello),
    path('slow_endpoint/', views.SlowEndpoint.as_view()),
]
