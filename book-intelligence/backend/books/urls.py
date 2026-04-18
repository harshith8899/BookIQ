from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.list_books),
    path('books/<int:id>/', views.book_detail),
    path('books/<int:id>/recommendations/', views.get_recommendations),  
    path('books/upload/', views.upload_book),
    path('books/ask/', views.ask_question),
    path('books/chat-history/', views.get_chat_history),
]