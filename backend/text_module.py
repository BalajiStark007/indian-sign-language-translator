# backend/text_module.py
import os
import json
import string
from typing import Tuple, List
import numpy as np

from rapidfuzz import process, fuzz

from sentence_transformers import SentenceTransformer, util

BASE_DIR = os.path.dirname(__file__)
with open(os.path.join(BASE_DIR, "config.json"), "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

EMBED_MODEL_NAME = CONFIG.get("embedding_model")
EMBED_THRESHOLD = CONFIG.get("embedding_threshold", 0.65)
FUZZY_THRESHOLD = CONFIG.get("fuzzy_threshold", 80)

# Load phrase list
PHRASES_PATH = os.path.join(BASE_DIR, CONFIG.get("isl_phrases_path", "isl_phrases.json"))
with open(PHRASES_PATH, "r", encoding="utf-8") as f:
    _phrases_data = json.load(f)
ISL_PHRASES = _phrases_data.get("phrases", [])

# Load embedding model lazily
_embedding_model = None
_phrase_embeddings = None

def _init_embeddings():
    global _embedding_model, _phrase_embeddings
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBED_MODEL_NAME)
    if _phrase_embeddings is None:
        _phrase_embeddings = _embedding_model.encode(ISL_PHRASES, convert_to_tensor=True)

def preprocess_text(text: str) -> str:
    if not text:
        return ""
    # remove punctuation, extra whitespace
    table = str.maketrans("", "", string.punctuation)
    t = text.translate(table)
    return " ".join(t.split()).lower()

def semantic_match(text: str) -> Tuple[str, float]:
    """
    Returns best phrase and similarity (0..1)
    """
    if not text:
        return "", 0.0
    _init_embeddings()
    q_emb = _embedding_model.encode(text, convert_to_tensor=True)
    hits = util.semantic_search(q_emb, _phrase_embeddings, top_k=1)
    if hits and hits[0]:
        idx = hits[0][0]["corpus_id"]
        score = hits[0][0]["score"]  # cosine similarity
        return ISL_PHRASES[idx], float(score)
    return "", 0.0

def fuzzy_match(text: str) -> Tuple[str, int]:
    match = process.extractOne(text, ISL_PHRASES, scorer=fuzz.token_sort_ratio)
    if match:
        phrase, score, _ = match
        return phrase, score
    return "", 0

def best_match(text: str) -> dict:
    """
    Returns dict: { "method": "embedding"|"fuzzy", "phrase":..., "score":... }
    """
    text = preprocess_text(text)
    # try embedding
    try:
        phrase, score = semantic_match(text)
        if score >= EMBED_THRESHOLD:
            return {"method": "embedding", "phrase": phrase, "score": score}
    except Exception as e:
        # fallback to fuzzy if embeddings fail
        pass

    # fuzzy fallback
    phrase_f, score_f = fuzzy_match(text)
    if score_f >= FUZZY_THRESHOLD:
        return {"method": "fuzzy", "phrase": phrase_f, "score": score_f}
    return {"method": "none", "phrase": "", "score": 0}
