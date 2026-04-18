from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Book Intelligence API is running 🚀")

urlpatterns = [
    path('', home),
    path('api/', include('books.urls')),
]