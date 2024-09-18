import re

class Translator:
    def __init__(self):
        self.tamil_pattern = re.compile(r'[\u0B80-\u0BFF]+')

    def detect_and_translate(self, text):
        if self.tamil_pattern.search(text):
            print(f"Detected Tamil: {text}")
            # Mock translation to English
            return 'ta', text  # In a real scenario, you'd translate to English here
        else:
            print(f"Detected English: {text}")
            return 'en', text

    def translate_text(self, text, target_language):
        if target_language == 'ta':
            print(f"Mock translation to Tamil: {text}")
        else:
            print(f"Mock translation to English: {text}")
        return text  # In a real scenario, you'd perform actual translation here