#!/bin/bash

# Install dependencies using the system's default python (from Vercel environment)
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Apply migrations
python manage.py migrate
