import argparse
import time
import requests
from rich.console import Console


def main() -> None:
    parser = argparse.ArgumentParser(description='Interroger la base RAG via l\'API')
    parser.add_argument('--endpoint', default='http://localhost:8180', help='URL de l\'API FastAPI')
    args = parser.parse_args()

    console = Console()
    console.print('[bold green]Bienvenue dans le CLI de requête RAG[/bold green]')
    console.print('Tapez [bold]quit[/bold] ou [bold]exit[/bold] pour quitter.')

    while True:
        question = console.input('\n[bold cyan]Question[/bold cyan]> ')
        if question.strip().lower() in {'quit', 'exit'}:
            console.print('Au revoir.')
            break
        if not question.strip():
            continue

        payload = {'query': question, 'top_k': 5}
        url = f"{args.endpoint.rstrip('/')}/query"
        start = time.time()
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            console.print(f'[bold red]Erreur HTTP:[/bold red] {exc}')
            continue

        elapsed = time.time() - start
        console.print(f'\n[bold]Réponse ([green]{elapsed:.2f}s[/green]):[/bold]')
        console.print(data.get('answer', 'Aucune réponse.'))

        if data.get('results'):
            console.print('\n[bold]Sources récupérées:[/bold]')
            for result in data['results']:
                console.print(f"- [yellow]{result.get('source')}[/yellow] (score={result.get('score'):.4f})")
                console.print(f"  {result.get('text')}\n")


if __name__ == '__main__':
    main()
