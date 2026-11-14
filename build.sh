#!/usr/bin/env bash
# Build do Render: instala dependências, coleta estáticos, migra e popula dados demo.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input
python manage.py seed
