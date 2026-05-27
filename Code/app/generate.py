import requests
from requests.exceptions import RequestException
from app.config import settings


class GenerationService:
    def __init__(self):
        self.ollama_host = settings.effective_ollama_host.rstrip("/")
        self.model_name = settings.ollama_model

    def answer(self, question: str, context: str, sources: list[str]) -> dict:
        system_prompt = (
            "Réponds à la question en utilisant uniquement le contexte fourni. "
            "Si la réponse n'est pas dans le contexte, dis que l'information n'est pas disponible."
        )

        prompt = (
            f"SYSTEM: {system_prompt}\n\n"
            f"CONTEXTE:\n{context}\n\n"
            f"QUESTION: {question}\n\n"
            f"CITES: {', '.join(sources)}\n\n"
            "RÉPONSE :"
        )

        url = f"{self.ollama_host}/api/generate"
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
            output = ""
            if "results" in data and data["results"]:
                output = data["results"][0].get("output", "")
            elif "choices" in data and data["choices"]:
                output = data["choices"][0].get("text", "")
            elif "completion" in data:
                output = data.get("completion", "")
            return {
                "answer": output or "Aucune réponse générée.",
                "model": self.model_name,
                "prompt_tokens": data.get("usage", {}).get("prompt_tokens"),
                "completion_tokens": data.get("usage", {}).get("completion_tokens"),
                "total_tokens": data.get("usage", {}).get("total_tokens"),
                "sources": sources,
            }
        except RequestException as exc:
            return {
                "answer": f"Erreur de génération : {exc}",
                "model": self.model_name,
                "sources": sources,
            }
