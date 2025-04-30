"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys

# Add virtual environment to sys.path
path = '/home/Ronnie123/myenv'  # Adjust to your virtualenv location
if path not in sys.path:
    sys.path.append(path)

# Add project path to sys.path
project_home = '/home/Ronnie123/New/project'  # Adjust to your project path
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
