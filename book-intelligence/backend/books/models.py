from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=300, blank=True)
    rating = models.CharField(max_length=50, blank=True)
    reviews = models.TextField(blank=True)
    description = models.TextField(blank=True)
    genre = models.CharField(max_length=100, blank=True)
    sentiment = models.CharField(max_length=50, blank=True)
    summary = models.TextField(blank=True)
    book_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    book_url = models.URLField(blank=True, null=True)


class ChatHistory(models.Model):
    question = models.TextField()
    answer = models.TextField()
    sources = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:50]