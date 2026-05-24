# RAG Knowledge Platform from Scratch

Ce projet est un système Retrieval-Augmented Generation local qui utilise PostgreSQL, MinIO, ChromaDB et FastAPI.

## Structure du projet

- `app/` : application FastAPI et services métier
- `dags/` : Airflow DAGs pour l'ingestion
- `scripts/` : utilitaires de génération et validation
- `expectations/` : suites Great Expectations
- `ollama/` : scripts de gestion du modèle LLM

## Démarrage rapide

1. Copier `.env.example` en `.env` ou utiliser le fichier `.env` déjà présent.
2. Installer les dépendances : `make setup`.
   - Si `make` n'est pas disponible sur Windows, utilisez `.\setup.ps1`.
3. Démarrer les services Docker : `docker compose up --build`.
   - Sur Windows, utilisez `.\docker-up.ps1`.
4. Lancer l'API localement (optionnel) : `make run-api`.
   - Sur Windows sans `make`, utilisez `.\run-api.ps1`.
5. Tester l'endpoint d'ingestion :
   - `curl -X POST http://localhost:8180/ingest -H "Content-Type: application/json" -d "{\"document_name\":\"sample.txt\",\"content\":\"Ceci est un document de test.\"}"
6. Tester l'endpoint de requête :
   - `curl -X POST http://localhost:8180/query -H "Content-Type: application/json" -d "{\"query\":\"Que contient le document ?\"}"`

## Objectifs

- ingestion de documents
- chunking et embeddings
- indexation vecteur
- requête RAG via FastAPI

## Prochaines étapes

- implémenter `app/config.py`
- créer le schéma PostgreSQL
- ajouter le pipeline d'ingestion
- configurer Docker Compose
