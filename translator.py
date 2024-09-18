import os

class Translator:
    def __init__(self):
        self.tamil = os.environ.get('TAMIL_LANGUAGE', 'Tamil')

    def translate_text(self, text, target_language):
        # This is a mock translation that just returns the original text
        if target_language == "en":
            print(f"Mock translation to English: {text}")
        elif target_language == "ta":
            print(f"Mock translation to {self.tamil}: {text}")
        return text