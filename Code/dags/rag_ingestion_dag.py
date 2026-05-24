from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator


def ingest_documents():
    # TODO: implémenter l'ingestion via pipeline Python
    print('Ingestion de documents')


def index_documents():
    # TODO: envoyer les chunks vers ChromaDB
    print('Indexation des documents')


def verify_data():
    # TODO: exécuter les validations Great Expectations
    print('Validation des données')


def notify():
    # TODO: notifier si le pipeline est terminé
    print('Notification de fin d\'exécution')

with DAG(
    dag_id='rag_ingestion',
    start_date=datetime(2025, 1, 1),
    schedule_interval='@daily',
    catchup=False,
    tags=['rag', 'ingestion'],
) as dag:
    task_ingest = PythonOperator(task_id='ingest_documents', python_callable=ingest_documents)
    task_index = PythonOperator(task_id='index_documents', python_callable=index_documents)
    task_verify = PythonOperator(task_id='verify_data', python_callable=verify_data)
    task_notify = PythonOperator(task_id='notify', python_callable=notify)

    task_ingest >> task_index >> task_verify >> task_notify
