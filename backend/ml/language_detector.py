"""
Language Detection Module
Uses langdetect with scikit-learn fallback for 5 supported languages:
Hindi, Kannada, English, Tamil, Telugu
"""

from langdetect import detect, detect_langs, LangDetectException
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import numpy as np
import re


# Language code mapping
LANGUAGE_MAP = {
    'hi': 'hindi',
    'kn': 'kannada',
    'en': 'english',
    'ta': 'tamil',
    'te': 'telugu'
}

LANGUAGE_CODE_MAP = {v: k for k, v in LANGUAGE_MAP.items()}

SUPPORTED_CODES = set(LANGUAGE_MAP.keys())

# Unicode ranges for Indic scripts (fallback detection)
SCRIPT_RANGES = {
    'hi': (0x0900, 0x097F),   # Devanagari (Hindi)
    'kn': (0x0C80, 0x0CFF),   # Kannada
    'ta': (0x0B80, 0x0BFF),   # Tamil
    'te': (0x0C00, 0x0C7F),   # Telugu
}


class LanguageDetector:
    """ML-powered language detection with script-based fallback."""

    def __init__(self):
        self._build_fallback_model()

    def _build_fallback_model(self):
        """Build a simple character-frequency classifier as fallback."""
        # Sample training data for each language
        training_data = {
            'hi': [
                "नमस्ते मैं हिंदी सीखना चाहता हूं",
                "मुझे प्रोग्रामिंग सिखाओ",
                "मैं पायथन सीखना चाहता हूँ",
                "कृपया मुझे जावास्क्रिप्ट के बारे में बताएं",
                "मशीन लर्निंग क्या है",
                "वेब डेवलपमेंट कैसे सीखें",
                "डाटा साइंस के बारे में बताइए",
                "मुझे कोडिंग सिखाइए",
            ],
            'kn': [
                "ನಮಸ್ಕಾರ ನಾನು ಕನ್ನಡ ಕಲಿಯಬೇಕು",
                "ನನಗೆ ಪ್ರೋಗ್ರಾಮಿಂಗ್ ಕಲಿಸಿ",
                "ಪೈಥಾನ್ ಕಲಿಯಲು ಬಯಸುತ್ತೇನೆ",
                "ಜಾವಾಸ್ಕ್ರಿಪ್ಟ್ ಬಗ್ಗೆ ಹೇಳಿ",
                "ಮೆಷಿನ್ ಲರ್ನಿಂಗ್ ಏನು",
                "ವೆಬ್ ಡೆವಲಪ್ಮೆಂಟ್ ಕಲಿಯುವುದು ಹೇಗೆ",
                "ಡೇಟಾ ಸೈನ್ಸ್ ಬಗ್ಗೆ ತಿಳಿಸಿ",
                "ನನಗೆ ಕೋಡಿಂಗ್ ಕಲಿಸಿ",
            ],
            'en': [
                "Hello I want to learn programming",
                "Teach me Python please",
                "I want to learn JavaScript",
                "Tell me about machine learning",
                "How to learn web development",
                "What is data science",
                "I need to learn coding",
                "Help me with React framework",
            ],
            'ta': [
                "வணக்கம் நான் தமிழ் கற்க வேண்டும்",
                "எனக்கு புரோகிராமிங் கற்பிக்கவும்",
                "பைதான் கற்க விரும்புகிறேன்",
                "ஜாவாஸ்கிரிப்ட் பற்றி சொல்லுங்கள்",
                "மெஷின் லர்னிங் என்றால் என்ன",
                "வெப் டெவலப்மென்ட் எப்படி கற்பது",
                "டேட்டா சயின்ஸ் பற்றி கூறுங்கள்",
                "எனக்கு கோடிங் கற்றுக்கொடுங்கள்",
            ],
            'te': [
                "నమస్కారం నేను తెలుగు నేర్చుకోవాలి",
                "నాకు ప్రోగ్రామింగ్ నేర్పించండి",
                "పైథాన్ నేర్చుకోవాలనుకుంటున్నాను",
                "జావాస్క్రిప్ట్ గురించి చెప్పండి",
                "మెషీన్ లెర్నింగ్ అంటే ఏమిటి",
                "వెబ్ డెవలప్‌మెంట్ ఎలా నేర్చుకోవాలి",
                "డేటా సైన్స్ గురించి తెలియజేయండి",
                "నాకు కోడింగ్ నేర్పించండి",
            ]
        }

        texts = []
        labels = []
        for lang, samples in training_data.items():
            texts.extend(samples)
            labels.extend([lang] * len(samples))

        self.vectorizer = TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(1, 3),
            max_features=5000
        )
        X = self.vectorizer.fit_transform(texts)
        self.classifier = MultinomialNB(alpha=0.1)
        self.classifier.fit(X, labels)

    def _detect_by_script(self, text):
        """Detect language based on Unicode script ranges."""
        script_counts = {lang: 0 for lang in SCRIPT_RANGES}

        for char in text:
            code_point = ord(char)
            for lang, (start, end) in SCRIPT_RANGES.items():
                if start <= code_point <= end:
                    script_counts[lang] += 1
                    break

        total_script_chars = sum(script_counts.values())

        if total_script_chars == 0:
            return 'en'  # Default to English if no Indic script detected

        # Return the language with most script characters
        detected = max(script_counts, key=script_counts.get)
        if script_counts[detected] > 0:
            return detected
        return 'en'

    def detect_language(self, text):
        """
        Detect the language of input text.
        Returns: dict with 'code', 'name', 'confidence'
        """
        if not text or not text.strip():
            return {
                'code': 'en',
                'name': 'english',
                'confidence': 0.0
            }

        text = text.strip()

        # Method 1: Try langdetect first
        try:
            detected = detect(text)
            langs = detect_langs(text)
            confidence = max(l.prob for l in langs)

            if detected in SUPPORTED_CODES:
                return {
                    'code': detected,
                    'name': LANGUAGE_MAP[detected],
                    'confidence': round(confidence, 3)
                }
        except LangDetectException:
            pass

        # Method 2: Unicode script detection (great for Indic languages)
        script_lang = self._detect_by_script(text)
        if script_lang != 'en' or not any(
            ord(c) > 127 for c in text
        ):
            if script_lang in SUPPORTED_CODES:
                return {
                    'code': script_lang,
                    'name': LANGUAGE_MAP[script_lang],
                    'confidence': 0.85
                }

        # Method 3: ML classifier fallback
        try:
            X = self.vectorizer.transform([text])
            prediction = self.classifier.predict(X)[0]
            proba = self.classifier.predict_proba(X)
            max_proba = float(np.max(proba))

            if prediction in SUPPORTED_CODES:
                return {
                    'code': prediction,
                    'name': LANGUAGE_MAP[prediction],
                    'confidence': round(max_proba, 3)
                }
        except Exception:
            pass

        # Default fallback: English
        return {
            'code': 'en',
            'name': 'english',
            'confidence': 0.5
        }


# Singleton instance
_detector = None

def get_detector():
    global _detector
    if _detector is None:
        _detector = LanguageDetector()
    return _detector


def detect_language(text):
    """Convenience function for language detection."""
    return get_detector().detect_language(text)
