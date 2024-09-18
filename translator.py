# translator.py

from google.cloud import translate_v2 as translate

class Translator:
    def __init__(self):
        self.client = translate.Client()

    def translate_text(self, text, target_language):
        result = self.client.translate(text, target_language=target_language)
        return result['translatedText']