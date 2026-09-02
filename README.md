# AI Language Translation Tool

> **Enterprise AI Language Translation & Speech Synthesis Platform**  
> A high-performance, modular AI translation suite featuring dual presentation layers (**Desktop GUI & Web API**), real-time reviewer analytics, gTTS multi-language speech streaming, and 1-click test presets.

---

## 🌟 Key Innovations for Reviewers & Recruiters

- **🚀 Dual Presentation Layer**:
  - **Native Desktop GUI**: Built with Python & `CustomTkinter` (`python main.py`).
  - **Web Dashboard**: Modern responsive web application running on **`http://localhost:5000`** (`python app_web.py`).
- **📊 Real-Time Analytics Dashboard**: Live counters tracking total translations, average response latency (`ms`), characters processed, and speech requests.
- **⚡ Latency Benchmarking**: Precise millisecond timer badge for every translation request.
- **🧪 1-Click Reviewer Test Presets**: Pre-configured sample prompts (*Business Email*, *Healthcare*, *Tech Resume*, *Travel & Greetings*) for instant testing without manual typing.
- **🔊 Multi-Language Audio Synthesis**: Asynchronous audio generation and streaming across 21 regional Indian & global languages via `gTTS`.
- **📥 Multi-Format Export**: Download formatted translation reports (`.txt`) and MP3 speech audio.
- **🛡️ API Resilience & Fallback Circuit Breaker**: Gracefully handles API key limits, network timeouts, or unconfigured environments without crashing.
- **📜 Session History Log**: Interactive history drawer storing recent translations with 1-click restore.

---

## 🛠️ Technology Stack & Architecture

- **Backend**: Python 3.10+, Flask REST API, Requests
- **Desktop UI**: CustomTkinter, Tkinter, PIL (Pillow)
- **Web UI**: HTML5, Tailwind CSS, FontAwesome 6, JavaScript (ES6)
- **APIs & Engines**: Google Cloud Translation API v2, gTTS (Google Text-to-Speech), Pygame Mixer
- **Architecture Pattern**: Asynchronous Threading, Modular Decoupled Controller-Service Design

---

## 📁 Project Structure

```text
LanguageTranslationTool/
│
├── app_web.py           # Flask Web Server & REST API endpoints
├── main.py              # Native desktop GUI application (CustomTkinter)
├── translator.py        # Google Cloud Translation API client & fallback engine
├── languages.py         # ISO 639-1 language mappings & helper functions
├── speech.py            # Async Text-to-Speech engine (gTTS + Pygame)
├── config.py            # Environment configuration, themes & app metadata
├── requirements.txt     # Python dependencies list
├── README.md            # Comprehensive documentation
├── .env                 # Local API key configuration (git-ignored)
├── .env.example         # Template for environment variables
├── .gitignore           # Git ignore rules
├── templates/
│   └── index.html       # Enterprise Web Dashboard HTML frontend
└── assets/
    ├── generate_icon.py # Icon generator utility script
    └── icon.ico         # Application icon
```

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### 2. Launch Localhost Web Server (Link: http://localhost:5000)
```powershell
python app_web.py
```

### 3. Launch Native Desktop GUI Application
```powershell
python main.py
```

---

## 🔑 Google Cloud Translation API Configuration (Optional)

Create or edit `.env` in the project root:

```ini
GOOGLE_TRANSLATE_API_KEY=AIzaSyYourActualGoogleCloudApiKeyHere
```

> **Note**: If `GOOGLE_TRANSLATE_API_KEY` is not provided in `.env`, the application automatically uses a fallback translation engine for immediate testing out of the box.

---

## 🏆 Summary of Features for Portfolio Review

| Feature | Highlight |
| :--- | :--- |
| **Recruiter Presets** | Test business, healthcare, and tech prompts in 1 click |
| **Speech Audio** | Listen to source & target text in 21 languages |
| **Performance** | Non-blocking async threading & live latency badge |
| **Export Options** | 1-click `.txt` report download & clipboard copy |
| **Design** | Dark / Light theme toggle & responsive modern layout |
