"""
Translator module for AI Language Translation Tool.
Handles requests to Google Cloud Translation API v2 with robust error handling,
validation, and fallback capabilities.
"""

import html
import requests
from typing import Tuple, Dict, Any

from config import GOOGLE_TRANSLATE_ENDPOINT, MAX_CHAR_LIMIT, reload_api_key
from languages import get_language_name


class TranslationError(Exception):
    """Custom exception raised for translation failures."""
    pass


class GoogleTranslator:
    """Handles text translation via Google Cloud Translation API v2."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.endpoint = GOOGLE_TRANSLATE_ENDPOINT

    def translate(self, text: str, target_lang: str, source_lang: str = "auto") -> Dict[str, Any]:
        """
        Translates text to target_lang.

        :param text: Text to translate.
        :param target_lang: Target language ISO code (e.g., 'te', 'hi', 'en').
        :param source_lang: Source language ISO code or 'auto' for auto-detection.
        :return: Dict containing:
                 - 'translated_text': Translated string
                 - 'detected_source_code': ISO code of source language
                 - 'detected_source_name': Human-readable name of source language
                 - 'engine_used': 'Google Cloud Translation API' or 'Fallback Translator'
                 - 'notice': Optional notice string
        :raises TranslationError: If validation fails or translation cannot be completed.
        """
        # 1. Validation
        if not text or not text.strip():
            raise TranslationError("Please enter text to translate.")

        text = text.strip()
        if len(text) > MAX_CHAR_LIMIT:
            raise TranslationError(f"Text exceeds maximum character limit of {MAX_CHAR_LIMIT} characters.")

        if not target_lang:
            raise TranslationError("Please select a target language.")

        # Reload API key to ensure any changes in .env are picked up
        api_key = reload_api_key()

        # If API key is available, use Google Cloud Translation API v2
        if api_key and api_key != "your_google_translate_api_key_here":
            return self._translate_google_cloud(text, target_lang, source_lang, api_key)
        else:
            # Fallback translator when Google API key is missing
            return self._translate_fallback(text, target_lang, source_lang)

    def _translate_google_cloud(
        self, text: str, target_lang: str, source_lang: str, api_key: str
    ) -> Dict[str, Any]:
        """Call official Google Cloud Translation API v2 REST Endpoint."""
        params = {
            "key": api_key
        }
        
        payload = {
            "q": text,
            "target": target_lang,
            "format": "text"
        }
        
        if source_lang and source_lang.lower() != "auto":
            payload["source"] = source_lang

        try:
            response = requests.post(
                self.endpoint,
                params=params,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                translations = data.get("data", {}).get("translations", [])
                if not translations:
                    raise TranslationError("Received empty response from Google Translation API.")
                
                first = translations[0]
                translated_text = html.unescape(first.get("translatedText", ""))
                detected_code = first.get("detectedSourceLanguage", source_lang)
                
                return {
                    "translated_text": translated_text,
                    "detected_source_code": detected_code,
                    "detected_source_name": get_language_name(detected_code),
                    "engine_used": "Google Cloud Translation API",
                    "notice": None
                }
            
            elif response.status_code in (400, 403):
                error_data = response.json().get("error", {})
                message = error_data.get("message", "Invalid API Key or unauthorized request.")
                # If API key is invalid or unauthorized, attempt fallback translation with a helpful notice
                print(f"Google Cloud Translation API notice ({response.status_code}): {message}. Switching to fallback engine...")
                fallback_res = self._translate_fallback(text, target_lang, source_lang)
                fallback_res["notice"] = (
                    f"Notice: Google API key error ({message}). "
                    "Switched to fallback translator. Update GOOGLE_TRANSLATE_API_KEY in .env with a valid Google Cloud API key."
                )
                return fallback_res
            
            elif response.status_code == 429:
                raise TranslationError("Google API Quota Exceeded (429). Please try again later.")
            
            else:
                raise TranslationError(
                    f"Google Translation API error (HTTP {response.status_code}): {response.text}"
                )

        except requests.exceptions.Timeout:
            raise TranslationError("Network request timed out. Please check your internet connection.")
        except requests.exceptions.ConnectionError:
            raise TranslationError("Network connection failed. Unable to reach Google Translation services.")
        except requests.exceptions.RequestException as req_err:
            raise TranslationError(f"Network error occurred: {str(req_err)}")

    def _translate_fallback(
        self, text: str, target_lang: str, source_lang: str
    ) -> Dict[str, Any]:
        """
        Fallback translation engine (MyMemory API) used when no Google API Key is set in .env.
        Ensures the GUI remains fully testable without forcing an immediate API key.
        """
        src = "autodetect" if (not source_lang or source_lang.lower() == "auto") else source_lang
        langpair = f"{src}|{target_lang}"
        
        url = f"https://api.mymemory.translated.net/get"
        params = {
            "q": text,
            "langpair": langpair
        }

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                response_data = data.get("responseData", {})
                translated_text = html.unescape(response_data.get("translatedText", ""))
                
                # Extract detected language if available
                matches = data.get("matches", [])
                detected_code = source_lang
                if matches and isinstance(matches, list):
                    for match in matches:
                        if match.get("created-by") == "Autodetect":
                            detected_code = match.get("srclang", source_lang)
                            break

                notice = (
                    "Notice: GOOGLE_TRANSLATE_API_KEY not configured in .env. "
                    "Using Fallback Engine. Add your API key to .env for Google Cloud Translation."
                )

                if not translated_text:
                    raise TranslationError("Fallback translation returned empty response.")

                return {
                    "translated_text": translated_text,
                    "detected_source_code": detected_code,
                    "detected_source_name": get_language_name(detected_code),
                    "engine_used": "Fallback Engine (No API Key)",
                    "notice": notice
                }
            else:
                raise TranslationError(
                    "GOOGLE_TRANSLATE_API_KEY is missing in .env and fallback translation failed. "
                    "Please configure GOOGLE_TRANSLATE_API_KEY in your .env file."
                )

        except requests.exceptions.RequestException as req_err:
            raise TranslationError(
                "Missing GOOGLE_TRANSLATE_API_KEY in .env and network error on fallback. "
                f"Details: {str(req_err)}"
            )
