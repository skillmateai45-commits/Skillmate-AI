"""
Text-to-Speech Engine
Generates audio responses using gTTS in the user's original language.
"""

from gtts import gTTS
import os
import hashlib
import time
import base64
import io


# Language code mapping for gTTS
GTTS_LANG_MAP = {
    'hindi': 'hi',
    'kannada': 'kn',
    'english': 'en',
    'tamil': 'ta',
    'telugu': 'te'
}

# Cache directory for generated audio
AUDIO_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'audio_cache')


class TTSEngine:
    """Text-to-Speech engine using gTTS with caching."""

    def __init__(self, cache_dir=None):
        self.cache_dir = cache_dir or AUDIO_CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_key(self, text, language):
        """Generate a unique cache key for the text+language combo."""
        content = f"{language}:{text}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def _get_cache_path(self, cache_key):
        """Get the file path for a cached audio file."""
        return os.path.join(self.cache_dir, f"{cache_key}.mp3")

    def generate_audio(self, text, language='english'):
        """
        Generate speech audio from text in the specified language.

        Args:
            text: Text to convert to speech
            language: Language name (e.g., 'hindi', 'english')

        Returns:
            dict with 'audio_base64' (base64 encoded MP3), 'language', 'cached'
        """
        if not text or not text.strip():
            return {
                'audio_base64': '',
                'language': language,
                'cached': False,
                'error': 'Empty text provided'
            }

        lang_code = GTTS_LANG_MAP.get(language, 'en')
        cache_key = self._get_cache_key(text, lang_code)
        cache_path = self._get_cache_path(cache_key)

        # Check cache first
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    audio_data = f.read()
                audio_b64 = base64.b64encode(audio_data).decode('utf-8')
                return {
                    'audio_base64': audio_b64,
                    'language': language,
                    'cached': True
                }
            except Exception:
                pass

        # Generate new audio
        try:
            tts = gTTS(text=text, lang=lang_code, slow=False)

            # Save to file cache
            tts.save(cache_path)

            # Read back as base64
            with open(cache_path, 'rb') as f:
                audio_data = f.read()

            audio_b64 = base64.b64encode(audio_data).decode('utf-8')

            return {
                'audio_base64': audio_b64,
                'language': language,
                'cached': False
            }

        except Exception as e:
            # Fallback: try with in-memory buffer
            try:
                tts = gTTS(text=text, lang=lang_code, slow=False)
                buffer = io.BytesIO()
                tts.write_to_fp(buffer)
                buffer.seek(0)
                audio_data = buffer.read()
                audio_b64 = base64.b64encode(audio_data).decode('utf-8')

                return {
                    'audio_base64': audio_b64,
                    'language': language,
                    'cached': False
                }
            except Exception as e2:
                return {
                    'audio_base64': '',
                    'language': language,
                    'cached': False,
                    'error': f'TTS generation failed: {str(e2)}'
                }

    def cleanup_cache(self, max_age_hours=24):
        """Remove cached audio files older than max_age_hours."""
        if not os.path.exists(self.cache_dir):
            return

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        for filename in os.listdir(self.cache_dir):
            filepath = os.path.join(self.cache_dir, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > max_age_seconds:
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass


# Singleton instance
_engine = None

def get_tts_engine():
    global _engine
    if _engine is None:
        _engine = TTSEngine()
    return _engine


def generate_audio(text, language='english'):
    """Convenience function for audio generation."""
    return get_tts_engine().generate_audio(text, language)
