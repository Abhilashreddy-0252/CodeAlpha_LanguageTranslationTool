"""
Language mappings and helper functions for AI Language Translation Tool.
Contains ISO language code mappings for major world and Indian regional languages.
"""

AUTO_DETECT_LABEL = "Auto Detect"

# Language Name to ISO 639-1 / Google Translate Language Code
LANGUAGES = {
    "Arabic": "ar",
    "Bengali": "bn",
    "Chinese (Simplified)": "zh-CN",
    "English": "en",
    "French": "fr",
    "German": "de",
    "Gujarati": "gu",
    "Hindi": "hi",
    "Italian": "it",
    "Japanese": "ja",
    "Kannada": "kn",
    "Korean": "ko",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Punjabi": "pa",
    "Portuguese": "pt",
    "Russian": "ru",
    "Spanish": "es",
    "Tamil": "ta",
    "Telugu": "te",
    "Urdu": "ur"
}

# Mapping from ISO code back to human-readable Name
CODE_TO_LANGUAGE = {code: name for name, code in LANGUAGES.items()}
CODE_TO_LANGUAGE["auto"] = AUTO_DETECT_LABEL

# Specific gTTS language code mappings if needed
GTTS_LANG_CODES = {
    "zh-CN": "zh-CN",
    "zh-TW": "zh-TW",
}

def get_source_languages():
    """Return list of language names for source dropdown including Auto Detect."""
    return [AUTO_DETECT_LABEL] + sorted(list(LANGUAGES.keys()))

def get_target_languages():
    """Return list of language names for target dropdown (excluding Auto Detect)."""
    return sorted(list(LANGUAGES.keys()))

def get_language_code(language_name: str) -> str:
    """
    Get ISO language code from display name.
    Returns 'auto' if language_name is 'Auto Detect'.
    """
    if language_name == AUTO_DETECT_LABEL:
        return "auto"
    return LANGUAGES.get(language_name, "en")

def get_language_name(language_code: str) -> str:
    """Get display name from ISO language code."""
    if not language_code or language_code.lower() == "auto":
        return AUTO_DETECT_LABEL
    return CODE_TO_LANGUAGE.get(language_code, language_code.upper())

def get_gtts_code(language_code: str) -> str:
    """Get language code compatible with gTTS."""
    return GTTS_LANG_CODES.get(language_code, language_code.split("-")[0].lower())
