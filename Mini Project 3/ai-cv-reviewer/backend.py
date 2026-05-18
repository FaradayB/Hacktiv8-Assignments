import io
import os
import pdfplumber
import google.generativeai as genai
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

genai.configure(api_key=GEMINI_API_KEY)
# Using gemini-3.1-flash-lite as it is fast and suitable for text analysis tasks
model = genai.GenerativeModel('gemini-3.1-flash-lite')

app = FastAPI(title="AI CV Reviewer API")

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract and clean text from PDF using pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    return text.strip()

def generate_evaluation_prompt(cv_text: str) -> str:
    """Generate the strict prompt for Gemini AI based on rules."""
    return f"""
You are an Expert AI Engineering Recruiter. Analyze the extracted resume text and evaluate the candidate for an AI Engineer role.

## Evaluation Rules
- Only score EXPLICITLY mentioned skills and experiences in the CV. Do not infer or assume based on job titles or company names.
- If a skill is absent, score it as 0. If it is present but not detailed, score it as 5. If it is present with specific examples or projects, score it as 10.
- For bonus criteria, only score if there is clear evidence of experience or knowledge. Do not give partial credit for vague mentions.
- Provide a brief justification for each score based on the CV content.
- Be consistent in scoring across all candidates to ensure a fair comparison.

## Scoring System
| Score | Meaning |
|-------|---------|
| 9-10  | Expert, production-level, multiple projects |
| 7-8   | Proficient, clear hands-on experience |
| 5-6   | Moderate, academic or personal projects only |
| 3-4   | Mentioned but minimal evidence |
| 0-2   | Absent or negligible |

## Evaluation Criteria (Score 0-10)
1. Python Programming (weight: 25%) - Core requirement. Look for Python projects, libraries used, code examples mentioned.
2. Machine Learning & Model Evaluation (weight: 25%) - Understanding of ML pipeline, metrics (accuracy, F1, AUC), cross-validation, etc.
3. ML Libraries Experience (weight: 20%) - Scikit-learn, TensorFlow, PyTorch, Keras, XGBoost, etc.
4. Deep Learning Concepts (weight: 15%) - Bonus. CNN, RNN, LSTM, Transformer architectures.
5. LLM & Generative AI (weight: 10%) - Bonus. Experience with GPT, LLaMA, Hugging Face, RAG, fine-tuning.
6. Prompt Engineering (weight: 5%) - Bonus. Knowledge of prompt design, chain-of-thought, few-shot prompting, etc.

## Candidate Resume Text:
{cv_text}

## Output Format (STRICT - MUST FOLLOW)
Respond STRICTLY in this structure using Bahasa Indonesia. DO NOT add extra sections, DO NOT change the format, DO NOT explain outside the template, DO NOT hallucinate missing skills.

---
### Ringkasan Kandidat
Nama: [Candidate Name in CAPITAL LETTERS]
Ringkasan:
[Brief 2-3 sentence overview of the candidate]
 
---
### Kelebihan (Strengths)
- [Strength 1 with evidence from CV]
- [Strength 2 with evidence from CV]
- [Strength 3 ...]
 
---
### Kekurangan (Weaknesses)
- [Weakness 1 with explanation]
- [Weakness 2 ...]
 
---
### Skor Penilaian
 
| Kriteria | Skor (0-10) | Keterangan |
|---|---|---|
| Python Programming | X/10 | ... |
| Machine Learning & Evaluasi Model | X/10 | ... |
| Pengalaman Library ML | X/10 | ... |
| Deep Learning Concepts (bonus) | X/10 | ... |
| LLM & Generative AI (bonus) | X/10 | ... |
| Prompt Engineering (bonus) | X/10 | ... |
 
---
### Skor Kesesuaian Akhir: XX/100
 
Kalkulasi:
- Python (25%): X x 2.5 = Y
- ML Knowledge (25%): X x 2.5 = Y
- ML Libraries (20%): X x 2.0 = Y
- Deep Learning (15%): X x 1.5 = Y
- LLM & GenAI (10%): X x 1.0 = Y
- Prompt Eng. (5%): X x 0.5 = Y
 
---
### Rekomendasi
[Clear recommendation: Highly Recommended / Recommended / Needs Development / Not Recommended]
[2-3 sentences explaining the recommendation and next steps]
---
"""

@app.post("/analyze-cv/")
async def analyze_cv(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF is allowed.")
    
    file_bytes = await file.read()
    
    # Validasi Ukuran File (Maksimal 5MB)
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File size exceeds the 5MB limit.")
    
    # 1. Ekstrak teks dari PDF
    try:
        cv_text = extract_text_from_pdf(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    if not cv_text:
        raise HTTPException(status_code=400, detail="Could not extract any text from the PDF. The file might be scanned or empty.")

    # 2. Kirim ke Gemini AI
    prompt = generate_evaluation_prompt(cv_text)
    
    try:
        response = model.generate_content(prompt)
        ai_evaluation = response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Evaluation failed: {str(e)}")
    
    return JSONResponse(content={"evaluation": ai_evaluation})

# Untuk menjalankan server: uvicorn backend:app --reload