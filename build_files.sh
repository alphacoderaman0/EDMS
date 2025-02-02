#!/bin/bash

# Ensure pip is available
python -m ensurepip --default-pip

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run Django collectstatic & migrations
python manage.py collectstatic --noinput
python manage.py migrate
