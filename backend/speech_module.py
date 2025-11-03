import json, os
import speech_recognition as sr
import whisper

BASE_DIR = os.path.dirname(__file__)
CONFIG = json.load(open(os.path.join(BASE_DIR, "config.json"), "r", encoding="utf-8"))

def transcribe_file(file_path: str):
    engine = CONFIG.get("stt_engine", "whisper")
    if engine == "whisper":
        model = whisper.load_model(CONFIG.get("whisper_model", "small"))
        result = model.transcribe(file_path)
        return result.get("text", "").lower().strip()
    elif engine == "google":
        r = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio = r.record(source)
        return r.recognize_google(audio).lower()
    else:
        return ""
