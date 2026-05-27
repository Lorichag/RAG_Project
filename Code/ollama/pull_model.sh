#!/usr/bin/env bash
set -e

type ollama >/dev/null 2>&1 || {
  echo "Ollama n'est pas installé. Installez Ollama avant de continuer."
  exit 1
}

echo "Vérification du service Ollama..."
if ! ollama status >/dev/null 2>&1; then
  echo "Ollama ne semble pas être en cours d'exécution. Lancez 'ollama serve' sur le système hôte."
fi

echo "Téléchargement du modèle llama3.2:3b..."
ollama pull llama3.2:3b

echo "Modèle téléchargé. Pour démarrer le service :"
echo "  ollama serve --model llama3.2:3b"
