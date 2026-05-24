# Exercices RAG

1. Comprendre les composants du système : Postgres, MinIO, ChromaDB, FastAPI, Airflow.
2. Implémenter `app/config.py` pour charger les variables d'environnement.
3. Construire le schéma PostgreSQL pour les documents et le suivi d'ingestion.
4. Écrire un pipeline d'ingestion qui crée des chunks, calcule des embeddings et stocke les vecteurs.
5. Ajouter un endpoint FastAPI `/query` pour récupérer des résultats et générer une réponse.
6. Configurer un DAG Airflow pour orchestrer l'ingestion et la validation.
7. Créer une suite Great Expectations pour vérifier la qualité des documents.
