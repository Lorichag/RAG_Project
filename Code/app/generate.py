import requests
from requests.exceptions import RequestException
from app.config import settings


class GenerationService:
    def __init__(self):
        self.ollama_host = settings.ollama_host.rstrip("/")
        self.model_name = settings.ollama_model

    def generate_answer(self, query: str, context: str) -> str:
        prompt = (
            "Utilise le contexte suivant pour répondre à la question.\n\n"
            f"Contexte :\n{context}\n\nQuestion : {query}\nRéponse :"
        )

        url = f"{self.ollama_host}/v1/completions"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": 0.2,
            "max_tokens": 256,
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                return "Aucune réponse générée."
            first_choice = choices[0]
            return first_choice.get("text", "")
        except RequestException as exc:
            return f"Erreur de génération : {exc}"
