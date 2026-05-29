from collections import Counter
from math import exp

from src.text_utils import tokenize, cosine_from_counters



def bleu_like(reference: str, candidate: str) -> float:
    # TODO(STAGE 2): Implement unigram precision with brevity penalty.
    ref_tokens = tokenize(reference)
    cand_tokens = tokenize(candidate)

    if not cand_tokens:
        return 0.0
    if not ref_tokens:
        return 1.0 if not cand_tokens else 0.0

    ref_counts = Counter(ref_tokens)
    cand_counts = Counter(cand_tokens)
    overlap = sum(min(cand_counts[t], ref_counts[t]) for t in cand_counts)

    precision = overlap / len(cand_tokens)

    c = len(cand_tokens)
    r = len(ref_tokens)
    bp = 1.0 if c > r else exp(1 - (r / c))
    return bp * precision

def _lcs_length(a: list[str], b: list[str]) -> int:
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        curr = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev = curr
    return prev[-1]


def rouge_l(reference: str, candidate: str) -> float:
    # TODO(STAGE 2): Implement ROUGE-L using longest common subsequence.
    ref_tokens = tokenize(reference)
    cand_tokens = tokenize(candidate)

    if not ref_tokens or not cand_tokens:
        return 0.0

    lcs = _lcs_length(ref_tokens, cand_tokens)
    precision = lcs / len(cand_tokens)
    recall = lcs / len(ref_tokens)

    if precision + recall == 0:
        return 0.0
    return (2 * precision * recall) / (precision + recall)


def meteor_like(reference: str, candidate: str) -> float:
    # TODO(STAGE 2): Implement simple F-score style METEOR approximation.
    ref_tokens = tokenize(reference)
    cand_tokens = tokenize(candidate)

    if not ref_tokens or not cand_tokens:
        return 0.0

    ref_counts = Counter(ref_tokens)
    cand_counts = Counter(cand_tokens)
    matches = sum(min(cand_counts[t], ref_counts[t]) for t in cand_counts)

    if matches == 0:
        return 0.0

    precision = matches / len(cand_tokens)
    recall = matches / len(ref_tokens)

    alpha = 0.9
    denom = alpha * precision + (1 - alpha) * recall
    if denom == 0:
        return 0.0
    return (precision * recall) / denom


def embedding_similarity_like(reference: str, candidate: str) -> float:
    # TODO(STAGE 2): Use lexical cosine or real embedding cosine.
    ref_tokens = tokenize(reference)
    cand_tokens = tokenize(candidate)
    if not ref_tokens or not cand_tokens:
        return 0.0
    return cosine_from_counters(Counter(ref_tokens), Counter(cand_tokens))

