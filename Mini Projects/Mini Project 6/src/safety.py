import re


REFUSAL_MESSAGE = (
    "Maaf, saya hanya dapat membantu pertanyaan terkait layanan purna jual, "
    "garansi, suku cadang, dan booking servis. Saya tidak dapat membantu permintaan tersebut."
)


# TODO(STAGE 1): Add toxic, prompt-injection, and off-topic rules.
TOXIC_PATTERNS = [
    r"\b(bodoh|tolol|goblok|bego|oon|dungu|kampret|bangsat|bajingan|brengsek)\b",
    r"\b(anjing|asu|bacot|kontol|memek|ngentot|jancok|keparat)\b",
    r"\b(stupid|idiot|moron|dumb|retard(?:ed)?)\b",
    r"\b(fuck(?:ing)?|shit(?:ty)?|bitch(?:es)?|asshole|bastard)\b",
    r"\b(kamu\s+(tolol|bodoh|goblok)|dasar\s+(tolol|bodoh|goblok))\b",
    r"\b(you('re| are)\s+(stupid|idiot|dumb)|shut\s+up)\b",
]
PROMPT_INJECTION_PATTERNS = [
    r"\b(ignore|abaikan|lupakan)\b.{0,60}\b(instruction|instruksi|aturan|rule|previous|sebelumnya)\b",
    r"\b(override|timpa|bypass|lewati)\b.{0,60}\b(safety|guardrail|policy|kebijakan|aturan)\b",
    r"\b(reveal|show|display|print|tampilkan|bocorkan|leak)\b.{0,60}\b(system prompt|prompt sistem|developer prompt|hidden prompt|secret)\b",
    r"\b(apa|what)\b.{0,40}\b(system prompt|instruksi sistem|instruksi rahasia|internal instruction)\b",
    r"\b(pretend|act as|berpura-pura|anggap)\b.{0,60}\b(you are|kamu adalah|tanpa batas|unfiltered)\b",
    r"\b(jailbreak|developer mode|dan mode|god mode|unrestricted)\b",
    r"\b(new instruction|instruksi baru|mulai sekarang|from now on)\b.{0,60}\b(ignore|abaikan|ikuti perintah ini saja)\b",
    r"\b(run|execute|jalankan)\b.{0,40}\b(command|script|kode|shell|terminal)\b",
]
IN_SCOPE_KEYWORDS = [
    "purna jual",
    "after sales",
    "aftersales",
    "garansi",
    "warranty",
    "klaim garansi",
    "suku cadang",
    "spare part",
    "servis",
    "service",
    "booking servis",
    "jadwal servis",
    "perbaikan",
    "repair",
]


def check_safety(query: str) -> dict:
    text = query.lower()

    # TODO(STAGE 1): Return {"allowed": False, "reason": "toxic_language"} for toxic inputs.
    for pattern in TOXIC_PATTERNS:
        if re.search(pattern, text):
            return {"allowed": False, "reason": "toxic_language"}

    # TODO(STAGE 1): Return {"allowed": False, "reason": "prompt_injection"} for injection attempts.
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, text):
            return {"allowed": False, "reason": "prompt_injection"}

    # TODO(STAGE 1): Return off_topic if the query is outside after-sales topics.
    if IN_SCOPE_KEYWORDS and not any(keyword in text for keyword in IN_SCOPE_KEYWORDS):
        return {"allowed": False, "reason": "off_topic"}

    return {"allowed": True, "reason": None}

