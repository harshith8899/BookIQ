from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = '__all__'

    def get_author(self, obj):
        return obj.author if obj.author else "Unknown"
