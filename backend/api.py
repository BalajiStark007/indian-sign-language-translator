# backend/api.py
import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from translator import translate_audio
from renderer import get_gif_url, letters_sequence
from text_module import preprocess_text, best_match

app = FastAPI(title="Speech-to-Sign API")

BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "assets"))

# Mount static paths
app.mount("/static/gifs", StaticFiles(directory=os.path.join(ASSETS_DIR, "ISL_Gifs")), name="gifs")
app.mount("/static/letters", StaticFiles(directory=os.path.join(ASSETS_DIR, "letters")), name="letters")

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/translate")
async def api_translate(file: UploadFile = File(...)):
    # save uploaded file
    suffix = os.path.splitext(file.filename)[1]
    if suffix.lower() not in [".wav", ".mp3", ".m4a", ".flac"]:
        raise HTTPException(status_code=400, detail="Audio format not supported. Use wav/mp3/m4a/flac.")
    dest = os.path.join(UPLOAD_DIR, file.filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        result = translate_audio(dest)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # augment render info with URLs
    render = result["render"]
    if render["type"] == "gif":
        render["url"] = get_gif_url(render["file"])
    elif render["type"] == "letters":
        render["urls"] = letters_sequence(render["file"])

    return JSONResponse(result)

@app.post("/api/translate_text")
async def api_translate_text(payload: dict):
    text = payload.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="text missing")
    match = best_match(preprocess_text(text))
    response = {"input_text": text, "match": match}
    return JSONResponse(response)

@app.get("/api/phrases")
def list_phrases():
    from text_module import ISL_PHRASES
    return {"phrases": ISL_PHRASES}
