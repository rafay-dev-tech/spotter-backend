import os
from django.core.asgi import get_asgi_application

# Set the default settings for Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eld_backend.settings")

# Get the ASGI application
application = get_asgi_application()

# Vercel expects 'app' or 'handler' to be defined here
app = application
