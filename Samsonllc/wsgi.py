"""
WSGI config for Samsonllc project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Samsonllc.settings")

# Render often skips ./start.sh and only runs `gunicorn Samsonllc.wsgi`.
# Run migrate + collectstatic once at startup when needed.
_project_root = Path(__file__).resolve().parent.parent
_static_root = _project_root / "staticfiles"
_startup_marker = _project_root / ".django_startup_complete"

if not _startup_marker.exists():
    import django
    from django.core.management import call_command

    django.setup()
    call_command("migrate", interactive=False, verbosity=1)
    if not _static_root.exists() or not any(_static_root.iterdir()):
        call_command("collectstatic", interactive=False, verbosity=1)
    _startup_marker.touch()

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
