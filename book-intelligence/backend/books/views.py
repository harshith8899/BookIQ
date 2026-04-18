from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Book, ChatHistory
from .serializers import BookSerializer

from .rag import answer_question, index_book


# 📚 GET /api/books/
@api_view(['GET'])
def list_books(request):
    books = Book.objects.all().order_by('-created_at')
    return Response(BookSerializer(books, many=True).data)

# 📖 GET /api/books/<id>/
@api_view(['GET'])
def book_detail(request, id):
    try:
        book = Book.objects.get(id=id)
        return Response(BookSerializer(book).data)
    except Book.DoesNotExist:
        return Response(
            {"error": "Book not found"},
            status=status.HTTP_404_NOT_FOUND
        )


# 🤖 POST /api/books/ask/
@api_view(['POST'])
def ask_question(request):
    """RAG Q&A endpoint"""
    question = request.data.get('question', '').strip()
    
    if not question:
        return Response(
            {"error": "Please provide a question."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = answer_question(question)
    
    # Save to chat history
    ChatHistory.objects.create(
        question=question,
        answer=result["answer"],
        sources=result["sources"]
    )
    
    return Response(result, status=status.HTTP_200_OK)


# 📜 GET /api/books/chat-history/
@api_view(['GET'])
def get_chat_history(request):
    """Return saved chat history"""
    history = ChatHistory.objects.order_by('-created_at')[:20]
    
    data = [
        {
            "question": h.question,
            "answer": h.answer,
            "sources": h.sources,
            "created_at": h.created_at
        }
        for h in history
    ]
    
    return Response(data)


# 📥 POST /api/books/upload/
@api_view(['POST'])
def upload_book(request):
    title = request.data.get('title')

    # Skip duplicates
    if Book.objects.filter(title=title).exists():
        return Response(
            {"message": "Book already exists"},
            status=status.HTTP_200_OK
        )

    serializer = BookSerializer(data=request.data)

    if serializer.is_valid():
        book = serializer.save()

        # 🤖 Generate AI insights
        if book.description:
            try:
                book.summary = generate_summary(book.description)
                book.genre = classify_genre(book.description)
                book.save()
                print(f"🤖 AI insights generated for: {book.title}")
            except Exception as e:
                print("AI error:", e)

        # 🧠 Index into RAG (VERY IMPORTANT)
        try:
            index_book(book)
            print(f"📊 Indexed book: {book.title}")
        except Exception as e:
            print("RAG error:", e)

        return Response(
            BookSerializer(book).data,
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_recommendations(request, id):
    try:
        book = Book.objects.get(id=id)

        # 🔥 Simple logic: same genre
        recommendations = Book.objects.filter(
            genre=book.genre
        ).exclude(id=id)[:5]

        return Response(
            BookSerializer(recommendations, many=True).data
        )

    except Book.DoesNotExist:
        return Response([], status=200)