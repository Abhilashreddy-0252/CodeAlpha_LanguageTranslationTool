"""
AI Language Translation Tool - Main GUI Application

Features:
- Desktop GUI using CustomTkinter
- Google Cloud Translation API integration with fallback
- gTTS Text-to-Speech audio playback
- Multi-language support with Auto-Detect
- Non-blocking background threading
- Light / Dark theme support
- Live character counter, Swap languages, Copy to Clipboard, Clear
- Comprehensive error handling and status notifications
"""

import sys
import os
import threading
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

# Add current folder to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import customtkinter as ctk

from config import (
    APP_NAME,
    APP_SUBTITLE,
    APP_VERSION,
    WINDOW_SIZE,
    MIN_WINDOW_SIZE,
    ICON_PATH,
    MAX_CHAR_LIMIT,
)
from languages import (
    get_source_languages,
    get_target_languages,
    get_language_code,
    get_language_name,
    AUTO_DETECT_LABEL,
)
from translator import GoogleTranslator, TranslationError
from speech import TextToSpeech


# Set CustomTkinter default appearance
ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")


class LanguageTranslationApp(ctk.CTk):
    """Main Application Window for AI Language Translation Tool."""

    def __init__(self):
        super().__init__()

        # App Configuration
        self.title(f"{APP_NAME} - v{APP_VERSION}")
        self.geometry(WINDOW_SIZE)
        self.minsize(*MIN_WINDOW_SIZE)

        # Set Window Icon if exists
        if ICON_PATH.exists():
            try:
                self.iconbitmap(str(ICON_PATH))
            except Exception:
                pass

        # Backend Engines
        self.translator = GoogleTranslator()
        self.speech_engine = TextToSpeech()

        # UI State Variables
        self.source_langs = get_source_languages()
        self.target_langs = get_target_languages()
        
        self.source_lang_var = ctk.StringVar(value=AUTO_DETECT_LABEL)
        self.target_lang_var = ctk.StringVar(value="Telugu")
        self.theme_var = ctk.StringVar(value="System")
        
        self.is_translating = False
        self.detected_source_code = None

        # Build GUI
        self._create_widgets()
        self._bind_events()
        self._update_char_count()

    def _create_widgets(self):
        """Construct all UI frames and widgets."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- 1. HEADER FRAME ---
        self.header_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("gray90", "gray17"))
        self.header_frame.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        header_subframe = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        header_subframe.grid(row=0, column=0, padx=20, pady=12, sticky="ew")

        # Title & Subtitle
        title_label = ctk.CTkLabel(
            header_subframe,
            text=f"🌐 {APP_NAME}",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w"
        )
        title_label.pack(side="left")

        subtitle_label = ctk.CTkLabel(
            header_subframe,
            text=f"  |  {APP_SUBTITLE}",
            font=ctk.CTkFont(size=14, slant="italic"),
            text_color=("gray40", "gray60"),
            anchor="w"
        )
        subtitle_label.pack(side="left")

        # Theme Selector (Right aligned)
        theme_frame = ctk.CTkFrame(header_subframe, fg_color="transparent")
        theme_frame.pack(side="right")

        ctk.CTkLabel(theme_frame, text="Theme:", font=ctk.CTkFont(size=12, weight="bold")).pack(
            side="left", padx=(0, 6)
        )
        self.theme_dropdown = ctk.CTkOptionMenu(
            theme_frame,
            values=["System", "Dark", "Light"],
            variable=self.theme_var,
            command=self._change_theme,
            width=100,
            height=30
        )
        self.theme_dropdown.pack(side="left")

        # --- 2. LANGUAGE SELECTION BAR ---
        self.lang_bar_frame = ctk.CTkFrame(self, corner_radius=10)
        self.lang_bar_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.lang_bar_frame.grid_columnconfigure((0, 2), weight=1)

        # Source Language Dropdown
        source_box = ctk.CTkFrame(self.lang_bar_frame, fg_color="transparent")
        source_box.grid(row=0, column=0, padx=15, pady=10, sticky="ew")

        ctk.CTkLabel(
            source_box, text="Source Language:", font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 4))
        self.source_dropdown = ctk.CTkOptionMenu(
            source_box,
            values=self.source_langs,
            variable=self.source_lang_var,
            dynamic_resizing=False,
            height=36,
            font=ctk.CTkFont(size=13)
        )
        self.source_dropdown.pack(fill="x")

        # Swap Languages Button
        self.swap_btn = ctk.CTkButton(
            self.lang_bar_frame,
            text="⇄ Swap",
            width=85,
            height=36,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            text_color=("black", "white"),
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._swap_languages
        )
        self.swap_btn.grid(row=0, column=1, padx=10, pady=(24, 10))

        # Target Language Dropdown
        target_box = ctk.CTkFrame(self.lang_bar_frame, fg_color="transparent")
        target_box.grid(row=0, column=2, padx=15, pady=10, sticky="ew")

        ctk.CTkLabel(
            target_box, text="Target Language:", font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 4))
        self.target_dropdown = ctk.CTkOptionMenu(
            target_box,
            values=self.target_langs,
            variable=self.target_lang_var,
            dynamic_resizing=False,
            height=36,
            font=ctk.CTkFont(size=13)
        )
        self.target_dropdown.pack(fill="x")

        # --- 3. MAIN CONTENT FRAME (Input & Output Text Areas) ---
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.content_frame.grid_columnconfigure((0, 1), weight=1, uniform="equal")
        self.content_frame.grid_rowconfigure(0, weight=1)

        # --- Left Side: Input Text Box ---
        self.input_card = ctk.CTkFrame(self.content_frame, corner_radius=10)
        self.input_card.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        self.input_card.grid_rowconfigure(1, weight=1)
        self.input_card.grid_columnconfigure(0, weight=1)

        # Input Header Label
        input_header_frame = ctk.CTkFrame(self.input_card, fg_color="transparent")
        input_header_frame.grid(row=0, column=0, padx=12, pady=(10, 5), sticky="ew")
        
        ctk.CTkLabel(
            input_header_frame,
            text="📝 Enter Text",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")

        # Character Counter Label
        self.char_counter_lbl = ctk.CTkLabel(
            input_header_frame,
            text=f"0 / {MAX_CHAR_LIMIT} chars",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray60")
        )
        self.char_counter_lbl.pack(side="right")

        # Input Text Box
        self.input_text_box = ctk.CTkTextbox(
            self.input_card,
            font=ctk.CTkFont(size=14),
            wrap="word",
            border_width=1,
            border_color=("gray75", "gray35")
        )
        self.input_text_box.grid(row=1, column=0, padx=12, pady=5, sticky="nsew")

        # Input Actions Frame (Listen Source, Clear Input)
        input_actions = ctk.CTkFrame(self.input_card, fg_color="transparent")
        input_actions.grid(row=2, column=0, padx=12, pady=(5, 10), sticky="ew")

        self.btn_speak_source = ctk.CTkButton(
            input_actions,
            text="🔊 Speak Input",
            width=110,
            height=32,
            fg_color=("gray80", "gray25"),
            hover_color=("gray70", "gray35"),
            text_color=("black", "white"),
            command=self._speak_source
        )
        self.btn_speak_source.pack(side="left", padx=(0, 6))

        self.btn_clear_input = ctk.CTkButton(
            input_actions,
            text="🗑️ Clear",
            width=90,
            height=32,
            fg_color=("gray80", "gray25"),
            hover_color=("gray70", "gray35"),
            text_color=("black", "white"),
            command=self._clear_input
        )
        self.btn_clear_input.pack(side="left")

        # --- Right Side: Output Text Box ---
        self.output_card = ctk.CTkFrame(self.content_frame, corner_radius=10)
        self.output_card.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")
        self.output_card.grid_rowconfigure(1, weight=1)
        self.output_card.grid_columnconfigure(0, weight=1)

        # Output Header Label
        output_header_frame = ctk.CTkFrame(self.output_card, fg_color="transparent")
        output_header_frame.grid(row=0, column=0, padx=12, pady=(10, 5), sticky="ew")

        self.output_header_lbl = ctk.CTkLabel(
            output_header_frame,
            text="✨ Translation Output",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.output_header_lbl.pack(side="left")

        # Output Text Box
        self.output_text_box = ctk.CTkTextbox(
            self.output_card,
            font=ctk.CTkFont(size=14),
            wrap="word",
            border_width=1,
            border_color=("gray75", "gray35")
        )
        self.output_text_box.grid(row=1, column=0, padx=12, pady=5, sticky="nsew")

        # Output Actions Frame (Listen Target, Copy, Clear All)
        output_actions = ctk.CTkFrame(self.output_card, fg_color="transparent")
        output_actions.grid(row=2, column=0, padx=12, pady=(5, 10), sticky="ew")

        self.btn_speak_target = ctk.CTkButton(
            output_actions,
            text="🔊 Speak Translation",
            width=135,
            height=32,
            fg_color=("gray80", "gray25"),
            hover_color=("gray70", "gray35"),
            text_color=("black", "white"),
            command=self._speak_target
        )
        self.btn_speak_target.pack(side="left", padx=(0, 6))

        self.btn_copy = ctk.CTkButton(
            output_actions,
            text="📋 Copy",
            width=85,
            height=32,
            fg_color="#10B981",
            hover_color="#059669",
            text_color="white",
            font=ctk.CTkFont(weight="bold"),
            command=self._copy_translation
        )
        self.btn_copy.pack(side="left", padx=(0, 6))

        self.btn_export = ctk.CTkButton(
            output_actions,
            text="📥 Export Report",
            width=115,
            height=32,
            fg_color="#6366F1",
            hover_color="#4F46E5",
            text_color="white",
            font=ctk.CTkFont(weight="bold"),
            command=self._export_report
        )
        self.btn_export.pack(side="left", padx=(0, 6))

        self.btn_clear_all = ctk.CTkButton(
            output_actions,
            text="🧹 Clear All",
            width=90,
            height=32,
            fg_color=("gray80", "gray25"),
            hover_color=("gray70", "gray35"),
            text_color=("black", "white"),
            command=self._clear_all
        )
        self.btn_clear_all.pack(side="right")

        # --- 4. ACTION BAR (Translate Button & Progress Bar) ---
        self.action_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.action_bar.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        self.action_bar.grid_columnconfigure(0, weight=1)

        self.translate_btn = ctk.CTkButton(
            self.action_bar,
            text="🚀 Translate Text",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=44,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            corner_radius=8,
            command=self._start_translation
        )
        self.translate_btn.grid(row=0, column=0, sticky="ew")

        # Progress Bar (Hidden by default)
        self.progress_bar = ctk.CTkProgressBar(self.action_bar, height=6)
        self.progress_bar.set(0)
        # Not gridded initially

        # --- 5. STATUS BAR ---
        self.status_bar = ctk.CTkFrame(self, height=32, corner_radius=0, fg_color=("gray85", "gray14"))
        self.status_bar.grid(row=4, column=0, sticky="ew", pady=(5, 0))
        self.status_bar.grid_columnconfigure(0, weight=1)

        self.status_lbl = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=ctk.CTkFont(size=12),
            anchor="w",
            padx=15
        )
        self.status_lbl.grid(row=0, column=0, sticky="w")

        # Engine Badge Label
        self.engine_lbl = ctk.CTkLabel(
            self.status_bar,
            text="Engine: Idle",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
            anchor="e",
            padx=15
        )
        self.engine_lbl.grid(row=0, column=1, sticky="e")

    def _bind_events(self):
        """Bind keyboard events and live character counter updates."""
        self.input_text_box.bind("<KeyRelease>", self._on_input_changed)
        # Ctrl+Enter shortcut for translation
        self.bind("<Control-Return>", lambda event: self._start_translation())

    def _on_input_changed(self, event=None):
        """Handle character count update when user types."""
        self._update_char_count()

    def _update_char_count(self):
        """Update live character counter label."""
        text = self.input_text_box.get("1.0", "end-1c")
        count = len(text)
        self.char_counter_lbl.configure(text=f"{count} / {MAX_CHAR_LIMIT} chars")
        
        if count > MAX_CHAR_LIMIT:
            self.char_counter_lbl.configure(text_color="#EF4444")
        else:
            self.char_counter_lbl.configure(text_color=("gray50", "gray60"))

    def _change_theme(self, choice: str):
        """Toggle application theme (Light, Dark, System)."""
        ctk.set_appearance_mode(choice)
        self.set_status(f"Theme set to {choice}", state_type="info")

    def _swap_languages(self):
        """Swap Source and Target selected languages and text contents."""
        src = self.source_lang_var.get()
        tgt = self.target_lang_var.get()

        # If source is Auto Detect, swap target to source label or default English
        if src == AUTO_DETECT_LABEL:
            new_src = tgt
            new_tgt = "English"
        else:
            new_src = tgt
            new_tgt = src

        self.source_lang_var.set(new_src)
        self.target_lang_var.set(new_tgt)

        # Swap text contents if target text exists
        input_text = self.input_text_box.get("1.0", "end-1c").strip()
        output_text = self.output_text_box.get("1.0", "end-1c").strip()

        if output_text:
            self.input_text_box.delete("1.0", "end")
            self.input_text_box.insert("1.0", output_text)

            self.output_text_box.delete("1.0", "end")
            if input_text:
                self.output_text_box.insert("1.0", input_text)

            self._update_char_count()
            self.set_status("Swapped languages and text content.", state_type="info")
        else:
            self.set_status("Swapped languages.", state_type="info")

    def _start_translation(self):
        """Initiate translation in a background thread."""
        if self.is_translating:
            return

        text = self.input_text_box.get("1.0", "end-1c").strip()
        
        # Validation checks
        if not text:
            self.set_status("⚠️ Please enter text to translate.", state_type="warning")
            messagebox.showwarning("Input Required", "Please enter some text in the source box to translate.")
            return

        if len(text) > MAX_CHAR_LIMIT:
            self.set_status(f"⚠️ Text exceeds {MAX_CHAR_LIMIT} character limit.", state_type="warning")
            messagebox.showwarning("Limit Exceeded", f"Text cannot exceed {MAX_CHAR_LIMIT} characters.")
            return

        source_name = self.source_lang_var.get()
        target_name = self.target_lang_var.get()

        source_code = get_language_code(source_name)
        target_code = get_language_code(target_name)

        if source_code != "auto" and source_code == target_code:
            self.set_status("⚠️ Source and Target languages are the same.", state_type="warning")

        # UI state during translation
        self.is_translating = True
        self.translate_btn.configure(state="disabled", text="⏳ Translating...")
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()

        self.set_status(f"Translating from {source_name} to {target_name}...", state_type="info")
        self.engine_lbl.configure(text="Engine: Connecting...")

        # Spawn worker thread
        thread = threading.Thread(
            target=self._translation_worker,
            args=(text, target_code, source_code),
            daemon=True
        )
        thread.start()

    def _translation_worker(self, text: str, target_code: str, source_code: str):
        """Background thread executing the translation request."""
        try:
            result = self.translator.translate(text, target_code, source_code)
            # Schedule GUI update on main thread
            self.after(0, self._on_translation_success, result)
        except TranslationError as err:
            self.after(0, self._on_translation_failure, str(err))
        except Exception as err:
            self.after(0, self._on_translation_failure, f"Unexpected error: {str(err)}")

    def _on_translation_success(self, result: dict):
        """Executed on main thread when translation succeeds."""
        self._stop_loading()

        translated_text = result["translated_text"]
        detected_name = result["detected_source_name"]
        engine_used = result["engine_used"]
        notice = result.get("notice")

        # Update output box
        self.output_text_box.delete("1.0", "end")
        self.output_text_box.insert("1.0", translated_text)

        # Update header label if Auto Detect was used
        if self.source_lang_var.get() == AUTO_DETECT_LABEL and detected_name:
            self.output_header_lbl.configure(
                text=f"✨ Translation Output (Detected: {detected_name})"
            )
        else:
            self.output_header_lbl.configure(text="✨ Translation Output")

        self.engine_lbl.configure(text=f"Engine: {engine_used}")

        if notice:
            self.set_status(f"✅ Translation complete! {notice}", state_type="warning")
        else:
            self.set_status(f"✅ Translation complete using {engine_used}.", state_type="success")

    def _on_translation_failure(self, error_msg: str):
        """Executed on main thread when translation fails."""
        self._stop_loading()
        self.set_status(f"❌ Error: {error_msg}", state_type="error")
        self.engine_lbl.configure(text="Engine: Failed")
        messagebox.showerror("Translation Error", error_msg)

    def _stop_loading(self):
        """Reset translation button and progress bar."""
        self.is_translating = False
        self.translate_btn.configure(state="normal", text="🚀 Translate Text")
        self.progress_bar.stop()
        self.progress_bar.grid_forget()

    def _speak_source(self):
        """Read source input text aloud using gTTS."""
        text = self.input_text_box.get("1.0", "end-1c").strip()
        if not text:
            self.set_status("⚠️ No source text to speak.", state_type="warning")
            return

        lang_name = self.source_lang_var.get()
        lang_code = get_language_code(lang_name)

        # If auto-detect, default to English for speech unless detected
        if lang_code == "auto":
            lang_code = self.detected_source_code or "en"

        self._start_speech(text, lang_code, label="Source")

    def _speak_target(self):
        """Read translation output text aloud using gTTS."""
        text = self.output_text_box.get("1.0", "end-1c").strip()
        if not text:
            self.set_status("⚠️ No translation output to speak.", state_type="warning")
            return

        lang_name = self.target_lang_var.get()
        lang_code = get_language_code(lang_name)

        self._start_speech(text, lang_code, label="Translation")

    def _start_speech(self, text: str, lang_code: str, label: str):
        """Helper to invoke speech engine asynchronously."""
        def on_start():
            self.after(0, lambda: self.set_status(f"🔊 Speaking {label} text...", state_type="info"))

        def on_finish():
            self.after(0, lambda: self.set_status("✅ Speech finished.", state_type="success"))

        def on_error(msg):
            self.after(0, lambda: self.set_status(f"❌ Speech Error: {msg}", state_type="error"))

        self.speech_engine.speak_async(
            text=text,
            lang_code=lang_code,
            on_start=on_start,
            on_finish=on_finish,
            on_error=on_error
        )

    def _copy_translation(self):
        """Copy translated text to OS clipboard."""
        text = self.output_text_box.get("1.0", "end-1c").strip()
        if not text:
            self.set_status("⚠️ Nothing to copy. Translation output is empty.", state_type="warning")
            return

        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()  # Required for clipboard persistence on Windows
        self.set_status("📋 Copied translation to clipboard!", state_type="success")

    def _export_report(self):
        """Export source text and translated text report to a .txt file."""
        import time
        from tkinter import filedialog
        input_text = self.input_text_box.get("1.0", "end-1c").strip()
        output_text = self.output_text_box.get("1.0", "end-1c").strip()
        
        if not input_text and not output_text:
            self.set_status("⚠️ Nothing to export. Enter text or translate.", state_type="warning")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Translation Report"
        )
        if file_path:
            content = f"""====================================================
AI LANGUAGE TRANSLATION REPORT
====================================================
Date / Time      : {time.strftime('%Y-%m-%d %H:%M:%S')}
Source Language  : {self.source_lang_var.get()}
Target Language  : {self.target_lang_var.get()}
Engine Used      : {self.engine_lbl.cget('text')}

----------------------------------------------------
SOURCE TEXT [INPUT]:
----------------------------------------------------
{input_text or '(Empty Input)'}

----------------------------------------------------
TRANSLATED TEXT [OUTPUT]:
----------------------------------------------------
{output_text or '(Empty Output)'}

====================================================
Generated by AI Language Translation Tool
====================================================
"""
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.set_status("📥 Exported translation report (.txt) successfully!", state_type="success")

    def _clear_input(self):
        """Clear only input text box."""
        self.input_text_box.delete("1.0", "end")
        self._update_char_count()
        self.set_status("Cleared input text.", state_type="info")

    def _clear_all(self):
        """Clear input, output, reset headers, and stop audio playback."""
        self.speech_engine.stop()
        self.input_text_box.delete("1.0", "end")
        self.output_text_box.delete("1.0", "end")
        self._update_char_count()
        self.output_header_lbl.configure(text="✨ Translation Output")
        self.set_status("Ready", state_type="info")
        self.engine_lbl.configure(text="Engine: Idle")

    def set_status(self, message: str, state_type: str = "info"):
        """Update status bar text and color based on state type."""
        color_map = {
            "info": ("gray20", "gray80"),
            "success": ("#047857", "#34D399"),
            "warning": ("#B45309", "#FBBF24"),
            "error": ("#B91C1C", "#F87171")
        }
        text_color = color_map.get(state_type, ("gray20", "gray80"))
        self.status_lbl.configure(text=message, text_color=text_color)


def main():
    """Launch Application."""
    app = LanguageTranslationApp()
    app.mainloop()


if __name__ == "__main__":
    main()
