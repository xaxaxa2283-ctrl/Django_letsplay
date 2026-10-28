"""Run from /app with python3 repair_site.py; no redeployment required."""
import os
import sys
import subprocess
import urllib.request
from pathlib import Path

root = Path.cwd()
if not (root / 'manage.py').is_file():
    raise RuntimeError('Run this script from the directory containing manage.py')
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'whitenoise==6.12.0'])
sys.path.insert(0, str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django_site2.settings')
import django
django.setup()
from django.core.management import call_command
from django.db import connection
from main.models import Product, Review

# Preserve an existing SQLite database before applying migrations.
import sqlite3
from datetime import datetime, timezone
backup_dir = root / 'recovery_backups' / ('repair-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
backup_dir.mkdir(parents=True, exist_ok=False)
if connection.vendor != 'sqlite':
    raise RuntimeError('Expected SQLite; stop and inspect database settings')
connection.ensure_connection()
backup = sqlite3.connect(str(backup_dir / 'db.sqlite3'))
try:
    connection.connection.backup(backup)
finally:
    backup.close()

call_command('migrate', interactive=False, verbosity=1)
# Existing importer skips reviews with the same name and text.
import import_reviews_prod
sources = [
    ('9d0d33294049256cebca5f64c840d3770b6a52fa', 'restore_catalog.py'),
    ('f2bfe5491ec4a5cdf6e768222c1afd759b6cff88', 'update_dock_photos.py'),
]
for commit, filename in sources:
    url = 'https://raw.githubusercontent.com/xaxaxa2283-ctrl/Django_letsplay/' + commit + '/' + filename
    with urllib.request.urlopen(url, timeout=60) as response:
        code = response.read()
    exec(compile(code, filename, 'exec'), {'__name__': '__catalog_recovery__'})

# Change settings last, so runserver's autoreloader sees the restored assets.
settings_file = root / 'Django_site2/settings.py'
original = settings_file.read_text(encoding='utf-8')
updated = original
if 'whitenoise.middleware.WhiteNoiseMiddleware' not in updated:
    marker = '    "django.middleware.security.SecurityMiddleware",'
    if marker not in updated:
        raise RuntimeError('Unexpected settings format; static middleware was not modified')
    updated = updated.replace(marker, marker + '\n    "whitenoise.middleware.WhiteNoiseMiddleware",', 1)
if 'WHITENOISE_USE_FINDERS' not in updated:
    updated += '\nWHITENOISE_USE_FINDERS = True\n'
if original != updated:
    (backup_dir / 'settings.py').write_text(original, encoding='utf-8')
    settings_file.write_text(updated, encoding='utf-8')
print('RECOVERY COMPLETE. Products:', Product.objects.count(), 'Reviews:', Review.objects.count())
print('Backup:', backup_dir)
print('Do not redeploy. Check the site after the development server reloads.')

