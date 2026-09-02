"""
Flask Web Interface for AI Language Translation Tool.
Runs local web server at http://localhost:5000 or http://127.0.0.1:5000.
Enhanced with recruiter analytics, sample presets, history tracking, and export features.
"""

import sys
import io
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, Response
from gtts import gTTS

# Add parent directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import APP_NAME, APP_SUBTITLE, APP_VERSION, MAX_CHAR_LIMIT
from languages import get_source_languages, get_target_languages, get_language_code, get_gtts_code, CODE_TO_LANGUAGE
from translator import GoogleTranslator, TranslationError

app = Flask(__name__, template_folder="templates", static_folder="static")
translator = GoogleTranslator()

# Global Analytics Counter for Reviewers & Metrics
SYSTEM_STATS = {
    "total_translations": 0,
    "total_characters": 0,
    "total_speech_requests": 0,
    "avg_latency_ms": 0.0,
    "language_usage": {}
}


@app.route("/")
def index():
    """Render Web Application Home Page."""
    sample_presets = [
        {
            "category": "💼 Business Email",
            "text": "Thank you for taking the time to review my profile. I am eager to contribute to your engineering team as an AI Developer.",
            "target": "Telugu"
        },
        {
            "category": "🏥 Healthcare",
            "text": "Please monitor your blood pressure daily, record your dosage, and consult your physician if symptoms persist.",
            "target": "Hindi"
        },
        {
            "category": "💻 Tech Resume",
            "text": "Full-stack AI developer experienced in Python, REST APIs, cloud services, asynchronous threading, and modern UI design.",
            "target": "Spanish"
        },
        {
            "category": "✈️ Travel & Greeting",
            "text": "Hello! Could you please guide me to the nearest train station and recommend a good local restaurant?",
            "target": "French"
        }
    ]

    return render_template(
        "index.html",
        app_name=APP_NAME,
        app_subtitle=APP_SUBTITLE,
        app_version=APP_VERSION,
        source_languages=get_source_languages(),
        target_languages=get_target_languages(),
        max_char_limit=MAX_CHAR_LIMIT,
        sample_presets=sample_presets,
        stats=SYSTEM_STATS
    )


@app.route("/api/translate", methods=["POST"])
def api_translate():
    """API endpoint to translate text with latency benchmarking and analytics."""
    start_time = time.time()
    try:
        data = request.get_json() or {}
        text = data.get("text", "").strip()
        source_name = data.get("source_lang", "Auto Detect")
        target_name = data.get("target_lang", "English")

        if not text:
            return jsonify({"success": False, "error": "Please enter text to translate."}), 400

        source_code = get_language_code(source_name)
        target_code = get_language_code(target_name)

        # Perform translation
        result = translator.translate(text, target_code, source_code)
        latency_ms = round((time.time() - start_time) * 1000, 2)

        # Update System Analytics
        SYSTEM_STATS["total_translations"] += 1
        SYSTEM_STATS["total_characters"] += len(text)
        SYSTEM_STATS["language_usage"][target_name] = SYSTEM_STATS["language_usage"].get(target_name, 0) + 1
        
        # Calculate moving average latency
        n = SYSTEM_STATS["total_translations"]
        SYSTEM_STATS["avg_latency_ms"] = round(
            ((SYSTEM_STATS["avg_latency_ms"] * (n - 1)) + latency_ms) / n, 2
        )

        return jsonify({
            "success": True,
            "translated_text": result["translated_text"],
            "detected_source_name": result.get("detected_source_name"),
            "detected_source_code": result.get("detected_source_code"),
            "engine_used": result.get("engine_used"),
            "notice": result.get("notice"),
            "latency_ms": latency_ms,
            "char_count": len(text),
            "stats": SYSTEM_STATS
        })

    except TranslationError as terr:
        return jsonify({"success": False, "error": str(terr)}), 400
    except Exception as err:
        return jsonify({"success": False, "error": f"Server error: {str(err)}"}), 500


@app.route("/api/tts", methods=["GET", "POST"])
def api_tts():
    """API endpoint to generate and stream Text-to-Speech audio in all languages."""
    try:
        if request.method == "POST":
            data = request.get_json() or {}
            text = data.get("text", "").strip()
            lang_param = data.get("lang", "en")
            detected_lang = data.get("detected_lang")
        else:
            text = request.args.get("text", "").strip()
            lang_param = request.args.get("lang", "en")
            detected_lang = request.args.get("detected_lang")

        if not text:
            return jsonify({"error": "No text provided for speech."}), 400

        # Convert display name or ISO code to ISO code
        lang_iso = get_language_code(lang_param)

        # Handle Auto Detect for speech input
        if lang_iso == "auto":
            if detected_lang and detected_lang != "auto":
                lang_iso = get_language_code(detected_lang)
            else:
                lang_iso = "en"

        gtts_lang = get_gtts_code(lang_iso)
        tts = gTTS(text=text, lang=gtts_lang, slow=False)

        SYSTEM_STATS["total_speech_requests"] += 1

        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)

        return send_file(
            fp,
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name="speech.mp3"
        )

    except Exception as err:
        return jsonify({"error": f"Audio synthesis failed for language '{lang_param}': {str(err)}"}), 500


@app.route("/api/export_file", methods=["POST"])
def api_export_file():
    """API endpoint to directly generate and stream a downloadable .txt report file."""
    try:
        if request.is_json:
            data = request.get_json() or {}
        else:
            data = request.form or {}

        source_text = data.get("source_text", "").strip()
        translated_text = data.get("translated_text", "").strip()
        source_lang = data.get("source_lang", "Auto Detect")
        target_lang = data.get("target_lang", "English")
        engine_used = data.get("engine_used", "Google Cloud / Fallback")
        latency = data.get("latency_ms", "N/A")

        if not source_text and not translated_text:
            return jsonify({"error": "No text provided to export."}), 400

        content = f"""====================================================
AI LANGUAGE TRANSLATION REPORT
====================================================
Date / Time      : {time.strftime('%Y-%m-%d %H:%M:%S')}
Source Language  : {source_lang}
Target Language  : {target_lang}
Engine Used      : {engine_used}
Response Latency : {latency}
Character Count  : {len(source_text)} characters

----------------------------------------------------
SOURCE TEXT [INPUT]:
----------------------------------------------------
{source_text if source_text else '(No Input Text Provided)'}

----------------------------------------------------
TRANSLATED TEXT [OUTPUT]:
----------------------------------------------------
{translated_text if translated_text else '(No Translated Output Provided)'}

====================================================
Generated by AI Language Translation Tool
====================================================
"""
        buf = io.BytesIO(content.encode("utf-8"))
        buf.seek(0)

        filename = f"Translation_Report_{int(time.time())}.txt"
        return send_file(
            buf,
            mimetype="text/plain; charset=utf-8",
            as_attachment=True,
            download_name=filename
        )
    except Exception as err:
        return jsonify({"error": f"Export failed: {str(err)}"}), 500


@app.route("/api/stats", methods=["GET"])
def api_stats():
    """API endpoint returning live reviewer analytics."""
    return jsonify(SYSTEM_STATS)


def main():
    port = int(os.environ.get("PORT", 5000))
    print(f"\n[+] Starting {APP_NAME} Web Server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
