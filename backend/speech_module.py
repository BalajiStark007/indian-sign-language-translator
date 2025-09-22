# backend/speech_module.py
import json
import os
from typing import Optional

from pydantic import BaseModel

# Load config
_config_path = os.path.join(os.path.dirname(__file__), "config.json")
with open(_config_path, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

STT_ENGINE = CONFIG.get("stt_engine", "whisper")

# Optional imports (import lazily)
def transcribe_whisper(file_path: str, model_name: str = None) -> Optional[str]:
    try:
        import whisper
    except Exception as e:
        raise RuntimeError("whisper not installed. pip install openai-whisper") from e
    model_name = model_name or CONFIG.get("whisper_model", "small")
    model = whisper.load_model(model_name)
    res = model.transcribe(file_path)
    return res.get("text", "").strip().lower()

def transcribe_vosk(file_path: str, lang: str = "en") -> Optional[str]:
    try:
        from vosk import Model, KaldiRecognizer
        import wave
    except Exception as e:
        raise RuntimeError("vosk not installed. pip install vosk") from e

    wf = wave.open(file_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        raise RuntimeError("Vosk expects 16bit mono WAV. Convert the file first.")
    model_dir = f"models/vosk-{lang}"
    if not os.path.exists(model_dir):
        raise RuntimeError(f"Vosk model not found at {model_dir}")

    model = Model(model_dir)
    rec = KaldiRecognizer(model, wf.getframerate())
    result = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            part = rec.Result()
            # extract text
            import json as j
            try:
                text = j.loads(part).get("text", "")
                result.append(text)
            except:
                pass
    final = rec.FinalResult()
    try:
        text = json.loads(final).get("text", "")
        result.append(text)
    except:
        pass
    return " ".join(result).strip().lower()

def transcribe_google(file_path: str) -> Optional[str]:
    # Simple fallback using speech_recognition against Google Cloud if configured.
    import speech_recognition as sr
    r = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio).lower()
    except Exception:
        return None

def transcribe_file(file_path: str) -> Optional[str]:
    engine = STT_ENGINE.lower()
    if engine == "whisper":
        return transcribe_whisper(file_path, CONFIG.get("whisper_model"))
    elif engine == "vosk":
        return transcribe_vosk(file_path)
    elif engine == "google":
        return transcribe_google(file_path)
    else:
        raise RuntimeError(f"Unknown STT engine {engine}")
