import csv
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from src.config import settings
from src.text_utils import chunk_text, tokenize, cosine_from_counters
from src.schemas import Source
from pypdf import PdfReader


@dataclass
class Chunk:
    chunk_id: str
    filename: str
    text: str
    tokens: list[str]


@dataclass
class RetrievedChunk:
    chunk_id: str
    filename: str
    text: str
    score: float


def read_pdf(path: Path) -> str:
    # TODO(STAGE 1): Use pypdf.PdfReader to extract text.
    reader = PdfReader(path)
    pages_text: list[str] = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text.strip():
            pages_text.append(page_text)
    return "\n".join(pages_text)


def read_csv(path: Path) -> str:
    # TODO(STAGE 1): Read CSV rows and convert each row into searchable text.
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return "\n".join(str(row) for row in reader)


def read_json(path: Path) -> str:
    # This helper is provided; you may improve formatting if useful.
    return json.dumps(json.loads(path.read_text(encoding="utf-8")), ensure_ascii=False)


def read_document(path: Path) -> str:
    # TODO(STAGE 1): Route by suffix: pdf, csv, json, txt/md.
    if path.suffix.lower() == ".pdf":
        return read_pdf(path)
    if path.suffix.lower() == ".csv":
        return read_csv(path)
    if path.suffix.lower() == ".json":
        return read_json(path)
    if path.suffix.lower() in {".txt", ".md"}:
        return path.read_text(encoding="utf-8")
    return ""


class LocalRetriever:
    def __init__(self, data_dir: Path | None = None, index_path: Path | None = None):
        self.data_dir = data_dir or settings.data_path
        self.index_path = index_path or settings.vector_path
        self.chunks: list[Chunk] = []

    def build(self) -> None:
        # TODO(STAGE 1): Load all local docs except gold_questions.csv, chunk, tokenize, and store chunks.
        self.chunks = []
        supported_suffixes = {".pdf", ".csv", ".json", ".txt", ".md"}

        chunk_number = 0
        for path in sorted(self.data_dir.rglob("*")):
            if not path.is_file():
                continue
            if path.name.lower() == "gold_questions.csv":
                continue
            if path.suffix.lower() not in supported_suffixes:
                continue

            doc_text = read_document(path)
            if not doc_text.strip():
                continue
            
            filename = str(path.relative_to(self.data_dir))
            chunks = chunk_text(doc_text)

            for index_in_file, text in enumerate(chunks):
                cleaned = text.strip()
                if not cleaned:
                    continue
                tokens = tokenize(cleaned)
                chunk_id = f"{path.stem}-{index_in_file}-{chunk_number}"

                self.chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        filename=filename,
                        text=cleaned,
                        tokens=tokens
                    )
                )
                chunk_number += 1

    def save(self) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"chunks": [asdict(chunk) for chunk in self.chunks]}
        self.index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self) -> bool:
        if not self.index_path.exists():
            return False
        payload = json.loads(self.index_path.read_text(encoding="utf-8"))
        self.chunks = [Chunk(**item) for item in payload.get("chunks", [])]
        return True

    def ensure_loaded(self) -> None:
        if not self.load():
            self.build()
            self.save()

    def search(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        self.ensure_loaded()
        query_tokens = tokenize(query)
        _ = query_tokens
        # TODO(STAGE 1): Score chunks and return top_k RetrievedChunk objects
        if not self.chunks:
            return []

        query_counter = Counter(query_tokens)
        scored: list[RetrievedChunk] = []

        for chunk in self.chunks:
            chunk_counter = Counter(chunk.tokens)
            score = cosine_from_counters(query_counter, chunk_counter)
            scored.append(
                RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    filename=chunk.filename,
                    text=chunk.text,
                    score=score,
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        k = top_k if top_k is not None else settings.top_k
        return scored[:k]
    
    def make_sources(self, chunks: list[RetrievedChunk]) -> list[Source]:
        return [
            Source(
                chunk_id=chunk.chunk_id,
                filename=chunk.filename,
                score=chunk.score,
            )
            for chunk in chunks
        ]


def build_index() -> None:
    retriever = LocalRetriever()
    retriever.build()
    retriever.save()


if __name__ == "__main__":
    build_index()
    print(f"Index written to {settings.vector_path}")

