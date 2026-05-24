import argparse
from app.retrieve import RetrievalService
from app.generate import GenerationService


def main() -> None:
    parser = argparse.ArgumentParser(description='Interroger la base RAG')
    parser.add_argument('--query', required=True, help='Question à poser')
    parser.add_argument('--top-k', type=int, default=5, help='Nombre de passages à récupérer')
    args = parser.parse_args()

    retriever = RetrievalService()
    generator = GenerationService()

    results = retriever.query(args.query, top_k=args.top_k)
    context = '\n'.join([item['text'] for item in results])
    answer = generator.generate_answer(args.query, context)

    print('--- Résultats ---')
    for item in results:
        print(item)
    print('\n--- Réponse ---')
    print(answer)


if __name__ == '__main__':
    main()
