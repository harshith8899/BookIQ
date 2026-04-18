# scraper/generate_insights.py
import os, sys, django

# Setup Django environment
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from books.models import Book
from books.ai_insights import generate_summary, classify_genre
import time

books = Book.objects.filter(summary="")  # only books without summaries

print(f"Generating insights for {books.count()} books...")

for book in books:
    if not book.description:
        print(f"⏭️  Skipping (no description): {book.title}")
        continue
    try:
        book.summary = generate_summary(book.title, book.description)
        book.genre = classify_genre(book.title, book.description)
        book.save()
        print(f"✅ Done: {book.title} → Genre: {book.genre}")
        time.sleep(0.5)  # avoid hitting API rate limits
    except Exception as e:
        print(f"❌ Error for {book.title}: {e}")

print("All done!")