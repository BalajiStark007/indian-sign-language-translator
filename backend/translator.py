# backend/translator.py
import os
from .speech_module import transcribe_file
from .text_module import best_match, preprocess_text

BASE_DIR = os.path.dirname(__file__)
with open(os.path.join(BASE_DIR, "config.json"), "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

GIFS_PATH = os.path.normpath(os.path.join(BASE_DIR, CONFIG.get("gifs_path", "../assets/ISL_Gifs")))
LETTERS_PATH = os.path.normpath(os.path.join(BASE_DIR, CONFIG.get("letters_path", "../assets/letters")))

def translate_audio(file_path: str) -> dict:
    """
    Returns: {
      "input_text": "...",
      "match": {"method":..., "phrase":..., "score":...},
      "render": {"type":"gif"|"letters"|"unknown", "file": "..." }
    }
    """
    text = transcribe_file(file_path)
    if not text:
        return {"input_text": "", "match": {"method":"none","phrase":"","score":0}, "render": {"type":"unknown", "file": None}}
    match = best_match(text)
    if match["phrase"]:
        gif_name = f"{match['phrase']}.gif"
        gif_path = os.path.join(GIFS_PATH, gif_name)
        if os.path.exists(gif_path):
            return {"input_text": text, "match": match, "render": {"type":"gif", "file": gif_name}}
    # fallback: return letters (string of alphabets)
    clean = preprocess_text(text)
    letters_exist = True
    # check at least one letter present
    for ch in clean:
        if ch.isalpha():
            if not os.path.exists(os.path.join(LETTERS_PATH, f"{ch}.jpg")):
                letters_exist = False
                break
    if letters_exist and any(c.isalpha() for c in clean):
        return {"input_text": text, "match": match, "render": {"type":"letters", "file": clean}}
    return {"input_text": text, "match": match, "render": {"type":"unknown", "file": None}}
