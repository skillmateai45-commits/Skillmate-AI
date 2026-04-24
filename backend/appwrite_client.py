"""
Appwrite Client Module
Handles interaction logging to Appwrite database.
Server-side SDK only — keys never exposed to frontend.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Appwrite configuration
APPWRITE_ENDPOINT = os.getenv('APPWRITE_ENDPOINT', 'https://cloud.appwrite.io/v1')
APPWRITE_PROJECT_ID = os.getenv('APPWRITE_PROJECT_ID', '')
APPWRITE_API_KEY = os.getenv('APPWRITE_API_KEY', '')
APPWRITE_DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID', 'skillmate_db')
APPWRITE_COLLECTION_ID = os.getenv('APPWRITE_COLLECTION_ID', 'interactions')


class AppwriteLogger:
    """Logs user interactions to Appwrite database."""

    def __init__(self):
        self.enabled = bool(APPWRITE_PROJECT_ID and APPWRITE_API_KEY)
        self.client = None
        self.databases = None

        if self.enabled:
            try:
                from appwrite.client import Client
                from appwrite.services.databases import Databases
                from appwrite.id import ID

                self.client = Client()
                self.client.set_endpoint(APPWRITE_ENDPOINT)
                self.client.set_project(APPWRITE_PROJECT_ID)
                self.client.set_key(APPWRITE_API_KEY)
                self.databases = Databases(self.client)
                self.ID = ID
                print("[Appwrite] Connected successfully")
            except Exception as e:
                print(f"[Appwrite] Init failed: {e}")
                self.enabled = False
        else:
            print("[Appwrite] Not configured — logging disabled")

    def log_interaction(self, input_text, detected_language, translated_text,
                       extracted_skill, resources=None):
        """
        Log an interaction to Appwrite.
        Fails silently — never blocks user experience.

        Args:
            input_text: Original user input
            detected_language: Detected language name
            translated_text: English translation
            extracted_skill: Extracted skill name
            resources: List of resource URLs
        """
        if not self.enabled:
            return {'logged': False, 'reason': 'Appwrite not configured'}

        try:
            resource_urls = []
            if resources:
                if isinstance(resources, dict):
                    for category in ['docs', 'youtube']:
                        for item in resources.get(category, []):
                            if isinstance(item, dict):
                                resource_urls.append(item.get('url', ''))
                    wiki = resources.get('wikipedia', '')
                    if wiki:
                        resource_urls.append(wiki)
                elif isinstance(resources, list):
                    resource_urls = resources

            # Limit to 10 URLs to avoid document size issues
            resource_urls = resource_urls[:10]

            document = self.databases.create_document(
                database_id=APPWRITE_DATABASE_ID,
                collection_id=APPWRITE_COLLECTION_ID,
                document_id=self.ID.unique(),
                data={
                    'input_text': str(input_text)[:500],
                    'detected_language': str(detected_language),
                    'translated_text': str(translated_text)[:500],
                    'extracted_skill': str(extracted_skill),
                    'resources': resource_urls,
                    'timestamp': datetime.now().isoformat()
                }
            )

            return {'logged': True, 'document_id': document.get('$id', '')}

        except Exception as e:
            print(f"[Appwrite] Log failed: {e}")
            return {'logged': False, 'reason': str(e)}

    def get_recent_interactions(self, limit=20):
        """Get recent interactions from Appwrite."""
        if not self.enabled:
            return []

        try:
            from appwrite.query import Query
            result = self.databases.list_documents(
                database_id=APPWRITE_DATABASE_ID,
                collection_id=APPWRITE_COLLECTION_ID,
                queries=[
                    Query.order_desc('$createdAt'),
                    Query.limit(limit)
                ]
            )
            return result.get('documents', [])
        except Exception as e:
            print(f"[Appwrite] Fetch failed: {e}")
            return []


# Singleton instance
_logger = None

def get_logger():
    global _logger
    if _logger is None:
        _logger = AppwriteLogger()
    return _logger


def log_interaction(**kwargs):
    """Convenience function for logging interactions."""
    return get_logger().log_interaction(**kwargs)
