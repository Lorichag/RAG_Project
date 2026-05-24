from pathlib import Path


def create_sample_documents(output_dir: str = 'data') -> None:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    sample = path / 'sample_document.txt'
    sample.write_text('Ceci est un document de test pour l\'ingestion RAG.\n'*20, encoding='utf-8')


if __name__ == '__main__':
    create_sample_documents()
    print('Documents générés dans le dossier data/')
