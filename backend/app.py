"""
SkillMate AI — Flask Backend Application
Main API server powering the ML/NLP pipeline.

Endpoints:
  POST /api/process     — Main pipeline: detect → translate → extract → TTS → resources
  GET  /api/languages   — List supported languages
  GET  /api/resources/<skill> — Get resources for a specific skill
  GET  /api/skills       — List all available skills
  GET  /api/health       — Health check
"""

import os
import sys
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize Flask app
app = Flask(__name__)

# CORS configuration - H-001 fix: restrict origins
frontend_url = os.getenv('FRONTEND_URL')
allowed_origins = []

if frontend_url:
    allowed_origins.append(frontend_url)

# Only add localhost for development
is_development = os.getenv('FLASK_ENV') == 'development' or os.getenv('FLASK_DEBUG') == '1'
if is_development:
    allowed_origins.extend(["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5000"])

if allowed_origins:
    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
else:
    # No CORS if FRONTEND_URL not configured
    CORS(app, resources={r"/api/*": {"origins": []}})

# Rate limiting - M-003 fix
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Security headers - L-001 fix
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

# Lazy imports for ML modules (loaded on first request)
_language_detector = None
_translator = None
_skill_extractor = None
_tts_engine = None
_resource_fetcher = None
_appwrite_logger = None


def get_language_detector():
    global _language_detector
    if _language_detector is None:
        from ml.language_detector import get_detector
        _language_detector = get_detector()
    return _language_detector


def get_translator():
    global _translator
    if _translator is None:
        from ml.translator import get_translator as _get_translator
        _translator = _get_translator()
    return _translator


def get_skill_extractor():
    global _skill_extractor
    if _skill_extractor is None:
        from ml.skill_extractor import get_extractor
        _skill_extractor = get_extractor()
    return _skill_extractor


def get_tts_engine():
    global _tts_engine
    if _tts_engine is None:
        from speech.tts_engine import get_tts_engine as _get_tts
        _tts_engine = _get_tts()
    return _tts_engine


def get_resource_fetcher():
    global _resource_fetcher
    if _resource_fetcher is None:
        from resources.resource_fetcher import get_fetcher
        _resource_fetcher = get_fetcher()
    return _resource_fetcher


def get_appwrite():
    global _appwrite_logger
    if _appwrite_logger is None:
        from appwrite_client import get_logger
        _appwrite_logger = get_logger()
    return _appwrite_logger


# ============================================================
# API Routes
# ============================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'service': 'SkillMate AI Backend',
        'version': '1.0.0'
    })


@app.route('/api/languages', methods=['GET'])
def list_languages():
    """List all supported languages."""
    return jsonify({
        'languages': [
            {'code': 'hi', 'name': 'Hindi', 'native': 'हिंदी'},
            {'code': 'kn', 'name': 'Kannada', 'native': 'ಕನ್ನಡ'},
            {'code': 'en', 'name': 'English', 'native': 'English'},
            {'code': 'ta', 'name': 'Tamil', 'native': 'தமிழ்'},
            {'code': 'te', 'name': 'Telugu', 'native': 'తెలుగు'}
        ]
    })


@app.route('/api/skills', methods=['GET'])
def list_skills():
    """List all available skills."""
    try:
        extractor = get_skill_extractor()
        skills = extractor.get_all_skills()
        return jsonify({'skills': skills})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/resources/<skill>', methods=['GET'])
def get_resources(skill):
    """Get learning resources for a specific skill."""
    try:
        fetcher = get_resource_fetcher()
        resources = fetcher.get_resources(skill)
        return jsonify(resources)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/process', methods=['POST'])
@limiter.limit("10 per minute")  # M-003 fix: stricter rate limit for expensive endpoint
def process_input():
    """
    Main processing pipeline:
    1. Detect language
    2. Translate to English
    3. Extract skill
    4. Generate TTS audio (in original language)
    5. Fetch resources
    6. Log to Appwrite
    """
    try:
        # Parse request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        text = data.get('text', '').strip()

        # Input validation - M-001 related fix
        if not text:
            return jsonify({'error': 'Text input is required'}), 400
        if len(text) > 2000:
            return jsonify({'error': 'Text input too long (max 2000 characters)'}), 400

        want_voice = data.get('voice', True)

        # Step 1: Language Detection
        detector = get_language_detector()
        lang_result = detector.detect_language(text)

        detected_language = lang_result['name']
        language_code = lang_result['code']
        language_confidence = lang_result['confidence']

        # Step 2: Translation to English
        translator = get_translator()
        translation_result = translator.translate_to_english(text, detected_language)
        translated_text = translation_result['translated_text']

        # Step 3: Skill Extraction (from English text)
        extractor = get_skill_extractor()
        skill_result = extractor.extract_skill(translated_text)

        skill_name = skill_result['skill']
        skill_category = skill_result['category']
        skill_description = skill_result['description']
        skill_confidence = skill_result['confidence']

        # Step 4: Generate TTS Audio (in the original language)
        audio_data = None
        if want_voice:
            try:
                tts = get_tts_engine()

                # Translate the skill description to the user's language for TTS
                if detected_language != 'english':
                    tts_text = translator.translate_from_english(
                        skill_description, detected_language
                    )
                else:
                    tts_text = skill_description

                audio_result = tts.generate_audio(tts_text, detected_language)
                if audio_result.get('audio_base64'):
                    audio_data = audio_result['audio_base64']
            except Exception as e:
                print(f"[TTS] Error: {e}")
                # TTS failure doesn't block the response

        # Step 5: Fetch Resources
        fetcher = get_resource_fetcher()
        resources = fetcher.get_resources(skill_name)

        # Step 6: Log to Appwrite (async-like, non-blocking)
        try:
            appwrite = get_appwrite()
            appwrite.log_interaction(
                input_text=text,
                detected_language=detected_language,
                translated_text=translated_text,
                extracted_skill=skill_name,
                resources=resources
            )
        except Exception as e:
            print(f"[Appwrite] Log error: {e}")
            # Appwrite failure doesn't block the response

        # Build response
        response = {
            'success': True,
            'input': {
                'text': text,
                'language': {
                    'name': detected_language,
                    'code': language_code,
                    'confidence': language_confidence
                }
            },
            'translation': {
                'english_text': translated_text,
                'from': detected_language,
                'to': 'english'
            },
            'skill': {
                'name': skill_name,
                'category': skill_category,
                'description': skill_description,
                'confidence': skill_confidence
            },
            'resources': {
                'docs': resources.get('docs', []),
                'youtube': resources.get('youtube', []),
                'wikipedia': resources.get('wikipedia', '')
            }
        }

        if audio_data:
            response['audio'] = {
                'base64': audio_data,
                'format': 'mp3',
                'language': detected_language
            }

        return jsonify(response)

    except Exception as e:
        # L-002 fix: Log detailed error internally, return generic message
        error_id = os.urandom(8).hex()
        print(f"[ERROR {error_id}] {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error_id': error_id,
            'message': 'An error occurred processing your request. Please try again.'
        }), 500


# ============================================================
# Error Handlers
# ============================================================

@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================
# Main Entry Point
# ============================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
