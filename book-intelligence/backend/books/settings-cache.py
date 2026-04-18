# Add this to your backend/settings.py

# ---------- Django Cache (in-memory, no Redis needed) ----------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'bookiq-cache',
    }
}

# ---------- MySQL Database ----------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bookiq',
        'USER': 'root',
        'PASSWORD': 'yourpassword',   # change this
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# ---------- CORS ----------
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

INSTALLED_APPS = [
    # ... default apps ...
    'corsheaders',
    'rest_framework',
    'books',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # must be first
    # ... rest of middleware ...
]
