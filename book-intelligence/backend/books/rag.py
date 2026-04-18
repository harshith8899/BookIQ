import chromadb
from sentence_transformers import SentenceTransformer
from .ai_insights import answer_question_simple

# ✅ Load embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# ✅ Persistent ChromaDB (correct)
chroma_client = chromadb.PersistentClient(path="./chroma_db")

collection = chroma_client.get_or_create_collection(
    name="books",
    metadata={"hnsw:space": "cosine"}
)


# ✅ Better chunking
def chunk_text(text, chunk_size=300, overlap=80):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# ✅ FIXED INDEXING
def index_book(book):
    print(f"🔍 INDEXING BOOK: {book.title}")

    # ⚠️ Ensure usable content
    full_text = f"""
    Title: {book.title}
    Author: {book.author or 'Unknown'}
    Genre: {book.genre or 'Unknown'}
    Description: {book.description or ''}
    Summary: {book.summary or ''}
    """.strip()

    if len(full_text.strip()) < 20:
        print("⚠️ Skipping empty/weak content")
        return

    chunks = chunk_text(full_text)

    embeddings = embedder.encode(chunks).tolist()

    ids = [f"book_{book.id}_chunk_{i}" for i in range(len(chunks))]

    metadatas = [
        {
            "book_id": str(book.id),
            "title": book.title,
            "author": book.author or "Unknown",
            "genre": book.genre or "Unknown",
        }
        for _ in chunks
    ]

    # ✅ Remove old entries
    try:
        existing = collection.get(where={"book_id": str(book.id)})
        if existing and existing.get("ids"):
            collection.delete(ids=existing["ids"])
    except Exception as e:
        print("Delete warning:", e)

    # ✅ Add to DB
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )

    print(f"📚 Indexed: {book.title} ({len(chunks)} chunks)")


# ✅ SEARCH FIX
def search_books(question, n_results=5):
    print(f"🔎 SEARCHING FOR: {question}")

    question_embedding = embedder.encode([question]).tolist()[0]

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    print("📊 RAW RESULTS:", results)

    return results


# ✅ IMPROVED RAG
def answer_question(question):
    results = search_books(question, n_results=5)

    # ❌ No results
    if not results.get("documents") or not results["documents"][0]:
        return {
            "answer": "No relevant books found for your question.",
            "sources": []
        }

    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]

    # ✅ Build stronger context
    context_parts = []
    for chunk, meta in zip(chunks, metadatas):
        context_parts.append(
            f"[Book: {meta['title']} | Genre: {meta['genre']}]\n{chunk}"
        )

    context = "\n\n".join(context_parts)

    print("🧠 CONTEXT USED:\n", context)

    # ✅ Deduplicate sources
    sources_dict = {}
    for meta in metadatas:
        sources_dict[meta["title"]] = {
            "title": meta["title"],
            "author": meta["author"],
            "genre": meta["genre"]
        }

    sources = list(sources_dict.values())

    # ✅ Generate answer
    try:
        answer = answer_question_simple(question, context)
    except Exception as e:
        print("LLM ERROR:", e)
        answer = context  # fallback

    return {
        "answer": answer,
        "sources": sources
    }


# ✅ REINDEX ALL BOOKS (IMPORTANT)
def index_all_books():
    from books.models import Book

    books = Book.objects.all()

    print(f"🚀 Indexing {books.count()} books...")

    for book in books:
        index_book(book)

    print("✅ All books indexed!")