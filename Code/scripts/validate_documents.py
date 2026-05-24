def validate_document_text(text: str) -> bool:
    # TODO: utiliser Great Expectations ou règles de qualité pour vérifier le document
    if not text.strip():
        return False
    return True


if __name__ == '__main__':
    sample = 'Texte de validation.'
    print('Valide' if validate_document_text(sample) else 'Invalide')
