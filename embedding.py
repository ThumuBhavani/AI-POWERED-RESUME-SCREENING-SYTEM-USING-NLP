from sentence_transformers import SentenceTransformer
import numpy as np

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")  # Lightweight
    return _model

def embed_text(s: str) -> np.ndarray:
    m = get_model()
    vec = m.encode([s], normalize_embeddings=True)
    return vec[0]
