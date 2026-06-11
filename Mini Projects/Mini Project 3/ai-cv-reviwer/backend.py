from fastapi import FastAPI, UploadFile, File, HTTPException
import PyPDF2
import google.generativeai as genai
import io
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI CV Analyzer API")

# --- KONFIGURASI API AI ---
API_KEY = os.getenv("API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemma-4-26b-a4b-it')

def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        raise Exception(f"Gagal membaca PDF: {e}")

@app.post("/analyze-cv/")
async def analyze_cv(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File harus berformat PDF")

    try:
        file_bytes = await file.read()
        cv_text = extract_text_from_pdf(file_bytes)
        
        if not cv_text.strip():
            raise HTTPException(status_code=400, detail="Tidak dapat mengekstrak teks.")

        # UPDATED PROMPT (English, Table Format, Spacing, and Content Below Headers)
        prompt = f"""
        You are a Senior Tech Recruiter specializing in AI and Data Science. Your task is to evaluate the provided CV/Resume for an "AI Engineer" position based on strict criteria, rules, and weighting.

        [Evaluation Scale]
        Rate each criterion on a scale of 1 to 10:
        - 1-3: Poor / Missing critical elements
        - 4-6: Average / Basic knowledge
        - 7-8: Strong / Solid professional experience
        - 9-10: Exceptional / Industry-leading expertise

        [Evaluation Rules]
        1. Base your evaluation STRICTLY on the provided CV text. Do not hallucinate or assume skills, experiences, or degrees that are not explicitly mentioned.
        2. Be highly critical and objective. High scores (8-10) require concrete proof of AI engineering implementation (e.g., deploying LLMs, RAG architectures, training complex models, MLOps), not just basic data analysis or taking online courses.
        3. The Final Score must be calculated accurately based on the exact weighted sum of the criteria.
        4. Recommendation Rule: The candidate is "Recommended" ONLY if the Final Score is 7.0 or higher. Otherwise, state "Not Recommended".
        5. IMPORTANT: Leave 1 to 2 blank lines (Enter) between each section in your output for readability.

        [Evaluation Rules]
        1. Base your evaluation STRICTLY on the provided CV text. Do not hallucinate or assume skills, experiences, or degrees that are not explicitly mentioned.
        2. Be highly critical and objective. High scores (8-10) require concrete proof of AI engineering implementation (e.g., deploying LLMs, RAG architectures, training complex models, MLOps), not just basic data analysis or taking online courses.
        3. The Final Score must be calculated accurately based on the exact weighted sum of the criteria.
        4. Recommendation Rule: The candidate is "Recommended" ONLY if the Final Score is 7.0 or higher. Otherwise, state "Not Recommended".
        5. IMPORTANT: Leave 1 to 2 blank lines (Enter) between each section in your output for readability.
        6. STRICTLY PROHIBITED: DO NOT output any internal thinking process, chain of thought, or <think> tags. Output ONLY the final evaluation format requested.
        
        CV Text:
        {cv_text}

        Provide your output STRICTLY in the following format without adding any introductory or concluding text:

        **Candidate Name**: [Extract candidate's full name]


        **Candidate Summary**:
        [Provide a 2 to 3-sentence professional summary of the candidate focusing on their AI capabilities]


        **Strengths**: 
        - [Point 1]
        - [Point 2]
        - [Point 3]


        **Weaknesses**: 
        - [Point 1]
        - [Point 2]
        - [Point 3]


        **Score Breakdown**:
        - Technical AI Skills: [Score]/10
        - Work Experience & Impact: [Score]/10
        - Portfolio & Contributions: [Score]/10
        - Education & Certifications: [Score]/10
        
        
        **Weight Calculation**:
        | Criteria | Score | Weight | Result |
        |---|---|---|---|
        | Technical AI Skills | [Score] | 0.40 | [Result] |
        | Work Experience & Impact | [Score] | 0.35 | [Result] |
        | Portfolio & Contributions | [Score] | 0.15 | [Result] |
        | Education & Certifications | [Score] | 0.10 | [Result] |
        
        
        **Final Score**: [Final Score] / 10


        **Recommendation Statement**: [Recommended / Not Recommended]


        **Reason for Recommendation**:
        [Provide exactly 2 to 3 sentences explaining why they are recommended or not, directly referencing their final score and key findings from the evaluation criteria]
        """
        
        response = model.generate_content(prompt)
        
        return {
            "status": "success",
            "ai_analysis": response.text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))