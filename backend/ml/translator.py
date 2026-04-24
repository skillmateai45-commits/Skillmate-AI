"""
Translation Module
Translates detected language text to English using deep-translator.
Also translates English text back to the detected language for TTS.
"""

from deep_translator import GoogleTranslator
import time


# Language code mapping
LANG_CODES = {
    'hindi': 'hi',
    'kannada': 'kn',
    'english': 'en',
    'tamil': 'ta',
    'telugu': 'te'
}


class TranslationService:
    """Handles text translation between supported languages."""

    def __init__(self):
        self._retry_count = 3
        self._retry_delay = 1

    def _translate_with_retry(self, text, src, dest):
        """Translate with retry logic for reliability."""
        for attempt in range(self._retry_count):
            try:
                translator = GoogleTranslator(source=src, target=dest)
                result = translator.translate(text)
                return result
            except Exception as e:
                if attempt < self._retry_count - 1:
                    time.sleep(self._retry_delay * (attempt + 1))
                else:
                    raise Exception(f"Translation failed after {self._retry_count} attempts: {str(e)}")

    def translate_to_english(self, text, source_language):
        """
        Translate text from source language to English.

        Args:
            text: Input text string
            source_language: Language name (e.g., 'hindi', 'tamil')

        Returns:
            dict with 'translated_text', 'source', 'target'
        """
        if not text or not text.strip():
            return {
                'translated_text': '',
                'source': source_language,
                'target': 'english'
            }

        # Already English — return as-is
        if source_language == 'english':
            return {
                'translated_text': text.strip(),
                'source': 'english',
                'target': 'english'
            }

        src_code = LANG_CODES.get(source_language, 'auto')

        translated = self._translate_with_retry(text, src=src_code, dest='en')

        return {
            'translated_text': translated,
            'source': source_language,
            'target': 'english'
        }

    def translate_from_english(self, text, target_language):
        """
        Translate English text to target language for TTS output.

        Args:
            text: English text string
            target_language: Target language name (e.g., 'hindi')

        Returns:
            Translated text string
        """
        if not text or not text.strip():
            return ''

        if target_language == 'english':
            return text.strip()

        dest_code = LANG_CODES.get(target_language, 'en')

        return self._translate_with_retry(text, src='en', dest=dest_code)


# Singleton instance
_service = None

def get_translator():
    global _service
    if _service is None:
        _service = TranslationService()
    return _service


def translate_to_english(text, source_language):
    """Convenience function for translation to English."""
    return get_translator().translate_to_english(text, source_language)


def translate_from_english(text, target_language):
    """Convenience function for translation from English."""
    return get_translator().translate_from_english(text, target_language)
