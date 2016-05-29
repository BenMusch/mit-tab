"""
WSGI config for mittab project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os, sys
sys.path.append('/var/www/tab')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mittab.settings")

from django.core.wsgi import get_wsgi_application
<<<<<<< HEAD
from dj_static import Cling, MediaCling
application = get_wsgi_application()
=======
from dj_static import Cling
application = Cling(get_wsgi_application())
>>>>>>> 7f6fe82f6f1d6c5e18faf566f0baab8344023560
