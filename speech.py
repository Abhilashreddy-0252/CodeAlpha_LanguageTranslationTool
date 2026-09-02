"""
Speech module for AI Language Translation Tool.
Uses gTTS (Google Text-to-Speech) and Pygame audio mixer to synthesize
and play audio asynchronously without blocking the desktop GUI.
"""

import os
import tempfile
import time
import threading
from gtts import gTTS
import pygame

from languages import get_gtts_code


class TextToSpeech:
    """Manages audio synthesis and playback in background threads."""

    def __init__(self):
        self._is_playing = False
        self._temp_files = []
        # Initialize pygame mixer
        try:
            pygame.mixer.init()
        except Exception:
            pass

    def speak_async(self, text: str, lang_code: str, on_start=None, on_finish=None, on_error=None):
        """
        Synthesize speech and play audio in a background thread.

        :param text: Text to read aloud.
        :param lang_code: ISO language code (e.g. 'te', 'hi', 'en').
        :param on_start: Optional callback when audio synthesis starts.
        :param on_finish: Optional callback when playback completes.
        :param on_error: Optional callback receiving error message if failure occurs.
        """
        thread = threading.Thread(
            target=self._speak_worker,
            args=(text, lang_code, on_start, on_finish, on_error),
            daemon=True
        )
        thread.start()

    def stop(self):
        """Stop current audio playback immediately."""
        try:
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
        except Exception:
            pass
        self._is_playing = False

    def _speak_worker(self, text: str, lang_code: str, on_start, on_finish, on_error):
        if not text or not text.strip():
            if on_error:
                on_error("No text available to speak.")
            return

        # Stop any currently playing audio
        self.stop()

        gtts_lang = get_gtts_code(lang_code)

        try:
            if on_start:
                on_start()

            # Synthesize audio with gTTS
            tts = gTTS(text=text.strip(), lang=gtts_lang, slow=False)

            # Create temporary MP3 file
            fd, temp_file_path = tempfile.mkstemp(suffix=".mp3", prefix="app_tts_")
            os.close(fd)

            tts.save(temp_file_path)
            self._temp_files.append(temp_file_path)

            # Play back via pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            pygame.mixer.music.load(temp_file_path)
            pygame.mixer.music.play()

            self._is_playing = True

            # Poll until playback finishes
            while pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                time.sleep(0.1)

            pygame.mixer.music.unload()
            self._cleanup_file(temp_file_path)

            if on_finish:
                on_finish()

        except ValueError:
            if on_error:
                on_error(f"Language '{gtts_lang}' is not supported by Text-to-Speech engine.")
        except Exception as err:
            if on_error:
                on_error(f"Speech playback error: {str(err)}")
        finally:
            self._is_playing = False

    def _cleanup_file(self, file_path: str):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            if file_path in self._temp_files:
                self._temp_files.remove(file_path)
        except Exception:
            pass
