#!/bin/bash
set -e

echo "🔄 Application des migrations..."
alembic upgrade head

echo "🌱 Chargement des données de démonstration..."
python -m scripts.seed_demo_data

echo "🚀 Démarrage du serveur API..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
