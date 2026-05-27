import argparse
import os
import sys

import pandas as pd
from dotenv import load_dotenv
from great_expectations.dataset import PandasDataset
from sqlalchemy import create_engine


def run_validation(verbose: bool = False) -> bool:
    load_dotenv()
    database_url = os.getenv('POSTGRES_DSN')
    if not database_url:
        print('POSTGRES_DSN manque dans l\'environnement.')
        return False

    engine = create_engine(database_url)
    df = pd.read_sql_table('document_chunks', con=engine)
    dataset = PandasDataset(df)

    expectations = [
        dataset.expect_table_columns_to_match_set(
            column_set={
                'id',
                'run_id',
                'object_name',
                'chunk_index',
                'char_start',
                'chunk_text',
                'chroma_id',
                'created_at',
            }
        ),
        dataset.expect_column_values_to_not_be_null(column='chunk_text'),
        dataset.expect_column_values_to_not_be_null(column='object_name'),
        dataset.expect_column_values_to_not_be_null(column='chroma_id'),
        dataset.expect_column_values_to_not_be_null(column='run_id'),
        dataset.expect_column_value_lengths_to_be_between(
            column='chunk_text', min_value=10, max_value=2000
        ),
        dataset.expect_column_values_to_match_regex(
            column='object_name', regex=r'^(raw|processed)/'
        ),
        dataset.expect_column_values_to_be_between(
            column='chunk_index', min_value=0, max_value=500
        ),
    ]

    success = True
    for result in expectations:
        if verbose:
            print(result)
        if not result['success']:
            success = False
            print(f"Échec de l'expectation: {result['expectation_config']['expectation_type']}")

    return success


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Valider les documents ingérés via Great Expectations')
    parser.add_argument('--verbose', action='store_true', help='Afficher les résultats détaillés')
    args = parser.parse_args()

    if run_validation(verbose=args.verbose):
        print('Validation réussie.')
        sys.exit(0)
    print('Validation échouée.')
    sys.exit(1)
