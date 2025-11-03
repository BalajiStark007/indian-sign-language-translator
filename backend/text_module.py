import json, os, string
from sentence_transformers import SentenceTransformer, util
from rapidfuzz import process, fuzz

BASE_DIR = os.path.dirname(__file__)
CONFIG = json.load(open(os.path.join(BASE_DIR, "config.json"), "r", encoding="utf-8"))
PHRASES_FILE = os.path.join(BASE_DIR, CONFIG["isl_phrases_path"])

PHRASES = json.load(open(PHRASES_FILE, "r", encoding="utf-8"))["phrases"]
model = SentenceTransformer(CONFIG["embedding_model"])
embeddings = model.encode(PHRASES, convert_to_tensor=True)

def preprocess(text):
    table = str.maketrans("", "", string.punctuation)
    return text.translate(table).strip().lower()

def best_match(text):
    query = preprocess(text)
    q_emb = model.encode(query, convert_to_tensor=True)
    hits = util.semantic_search(q_emb, embeddings, top_k=1)
    if hits and hits[0][0]["score"] >= CONFIG["embedding_threshold"]:
        idx = hits[0][0]["corpus_id"]
        return PHRASES[idx], hits[0][0]["score"]
    phrase, score, _ = process.extractOne(query, PHRASES, scorer=fuzz.token_sort_ratio)
    return phrase, score
