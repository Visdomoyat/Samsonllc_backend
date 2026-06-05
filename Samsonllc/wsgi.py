"""
WSGI config for Samsonllc project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Samsonllc.settings")

# Render often runs `gunicorn Samsonllc.wsgi` without ./start.sh, so staticfiles
# may never be built. Collect once when the output folder is missing.
_static_root = Path(__file__).resolve().parent.parent / "staticfiles"
if not _static_root.exists() or not any(_static_root.iterdir()):
    import django
    from django.core.management import call_command

    django.setup()
    call_command("collectstatic", interactive=False, verbosity=1)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
