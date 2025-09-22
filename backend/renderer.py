# backend/renderer.py
import os
from typing import List

BASE_DIR = os.path.dirname(__file__)
with open(os.path.join(BASE_DIR, "config.json"), "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

GIFS_PATH = os.path.normpath(os.path.join(BASE_DIR, CONFIG.get("gifs_path", "../assets/ISL_Gifs")))
LETTERS_PATH = os.path.normpath(os.path.join(BASE_DIR, CONFIG.get("letters_path", "../assets/letters")))

def get_gif_url(filename: str) -> str:
    # For FastAPI static mount, we assume /static/gifs/<filename>
    return f"/static/gifs/{filename}"

def letters_sequence(text: str) -> List[str]:
    # return list of relative URLs for letters
    letters = []
    for ch in text:
        if ch.isalpha():
            fname = f"{ch}.jpg"
            if os.path.exists(os.path.join(LETTERS_PATH, fname)):
                letters.append(f"/static/letters/{fname}")
    return letters
