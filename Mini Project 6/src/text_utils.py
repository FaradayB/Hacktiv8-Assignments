import math
import re
from collections import Counter


TOKEN_RE = re.compile(r"[A-Za-z0-9]+", re.UNICODE)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def estimate_tokens(text: str) -> int:
    return max(1, math.ceil(len(text) / 4))


def cosine_from_counters(a: Counter, b: Counter) -> float:
    # TODO(STAGE 1): Implement cosine similarity for sparse lexical vectors.
    if not a or b: 
        return 0.0
    dot = 0.0
    for token, a_val in a.items():
        dot += a_val * b.get(token, 0)
    
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))

    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot/(norm_a*norm_b)


def chunk_text(text: str, chunk_size: int = 850, overlap: int = 120) -> list[str]:
    # TODO(STAGE 1): Split long documents into overlapping chunks.
    text = normalize_text(text)
    if not text:
        return []
    
    if len(text) <= chunk_size:
        return [text]
    
    step = max(1, chunk_size - overlap)
    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk: 
            chunks.append(chunk)
        if end >= len(text):
            break
        start+=step

    return chunks

