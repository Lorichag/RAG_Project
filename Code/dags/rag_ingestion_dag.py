from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from app.ingest import IngestPipeline
from app.minio_store import MinIOStore
from scripts.validate_documents import validate_document_text


def list_pending_documents(**context):
    store = MinIOStore()
    pending = store.list_raw_documents()
    context['ti'].xcom_push(key='pending_documents', value=pending)
    print(f'Pending documents: {pending}')


def validate_documents(**context):
    pending = context['ti'].xcom_pull(key='pending_documents', task_ids='list_pending_documents') or []
    failed = []
    for name in pending:
        sample = f'Document {name} ready for validation.'
        if not validate_document_text(sample):
            failed.append(name)
    if failed:
        raise RuntimeError(f'Validation failed for: {failed}')
    context['ti'].xcom_push(key='validated_documents', value=pending)


def ingest_documents(**context):
    pending = context['ti'].xcom_pull(key='validated_documents', task_ids='validate_documents') or []
    pipeline = IngestPipeline()
    results = []
    for object_name in pending:
        try:
            result = pipeline.run_document(object_name)
            results.append(result.document_id)
        except Exception as exc:
            print(f'Failed to ingest {object_name}: {exc}')
    context['ti'].xcom_push(key='ingested_documents', value=results)


def log_summary(**context):
    ingested = context['ti'].xcom_pull(key='ingested_documents', task_ids='ingest_documents') or []
    print(f'Ingestion summary: {len(ingested)} documents ingested')


with DAG(
    dag_id='rag_ingestion_pipeline',
    start_date=datetime(2025, 1, 1),
    schedule_interval='@daily',
    catchup=False,
    default_args={
        'retries': 2,
        'retry_delay': timedelta(minutes=1),
    },
    tags=['rag', 'ingestion'],
) as dag:
    task_list = PythonOperator(task_id='list_pending_documents', python_callable=list_pending_documents)
    task_validate = PythonOperator(task_id='validate_documents', python_callable=validate_documents)
    task_ingest = PythonOperator(task_id='ingest_documents', python_callable=ingest_documents)
    task_summary = PythonOperator(task_id='log_summary', python_callable=log_summary)

    task_list >> task_validate >> task_ingest >> task_summary
