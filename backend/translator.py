import os, json
from backend.speech_module import transcribe_file
from backend.text_module import best_match, preprocess

BASE_DIR = os.path.dirname(__file__)
CONFIG = json.load(open(os.path.join(BASE_DIR, "config.json"), "r", encoding="utf-8"))
GIFS = os.path.normpath(os.path.join(BASE_DIR, CONFIG["gifs_path"]))
LETTERS = os.path.normpath(os.path.join(BASE_DIR, CONFIG["letters_path"]))

def translate_audio(file_path):
    text = transcribe_file(file_path)
    phrase, score = best_match(text)
    gif_path = os.path.join(GIFS, f"{phrase}.gif")
    if os.path.exists(gif_path):
        return {"input_text": text, "match": phrase, "gif": f"/static/gifs/{phrase}.gif"}
    else:
        letters = [f"/static/letters/{c}.jpg" for c in preprocess(text) if c.isalpha()]
        return {"input_text": text, "match": phrase, "letters": letters}
