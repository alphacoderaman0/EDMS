#!/bin/bash
# Optional local/CI helper. Vercel runs collectstatic automatically for Django.
set -e
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --noinput
