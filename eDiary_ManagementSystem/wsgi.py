"""
WSGI config for eDiary_ManagementSystem project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eDiary_ManagementSystem.settings')

application = get_wsgi_application()
# Vercel / some WSGI hosts look for `app`
app = application
