from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import shutil, os
from backend.translator import translate_audio
from fastapi.middleware.cors import CORSMiddleware


BASE_DIR = os.path.dirname(__file__)
ASSETS = os.path.normpath(os.path.join(BASE_DIR, "..", "assets"))
FRONTEND_BUILD = os.path.normpath(os.path.join(BASE_DIR, "..", "frontend", "react_app", "build"))

app = FastAPI(title="Speech to ISL Translator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static/gifs", StaticFiles(directory=os.path.join(ASSETS, "ISL_Gifs")), name="gifs")
app.mount("/static/letters", StaticFiles(directory=os.path.join(ASSETS, "letters")), name="letters")

if os.path.exists(FRONTEND_BUILD):
    app.mount("/", StaticFiles(directory=FRONTEND_BUILD, html=True), name="frontend")

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/translate")
async def translate(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1].lower()
    if suffix not in [".wav", ".mp3", ".m4a", ".flac"]:
        raise HTTPException(status_code=400, detail="Invalid audio format")
    dest = os.path.join(UPLOAD_DIR, file.filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    result = translate_audio(dest)
    return JSONResponse(result)

@app.get("/{path_name:path}")
async def serve_frontend(path_name: str):
    index_path = os.path.join(FRONTEND_BUILD, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"detail": "Frontend not built"}
