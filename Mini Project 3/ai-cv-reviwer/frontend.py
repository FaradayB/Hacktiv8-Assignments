import streamlit as st
import requests
import re

# Konfigurasi Halaman (Harus di baris paling atas)
st.set_page_config(
    page_title="AI Recruiter Pro | CV Evaluator", 
    page_icon="💼", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS UNTUK TAMPILAN PROFESIONAL ---
st.markdown("""
    <style>
        /* Menyembunyikan menu default Streamlit untuk kesan aplikasi mandiri */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Kustomisasi Tombol */
        .stButton>button {
            width: 100%;
            background-color: #0F52BA;
            color: white;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: bold;
            border: none;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #083D8D;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            color: white;
        }
        
        /* Menyesuaikan padding atas */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# Konfigurasi URL Backend FastAPI
BACKEND_URL = "http://127.0.0.1:8000/analyze-cv/"

# --- SIDEBAR (Panel Kiri) ---
with st.sidebar:
    st.title("🤖 AI Recruiter Pro")
    st.caption("Powered by Gemini 1.5 Flash & FastAPI")
    st.divider()
    
    st.markdown("### 📌 Informasi Loker")
    st.text_input("Posisi Target", value="AI Engineer", disabled=True)
    st.text_input("Departemen", value="Data & Engineering", disabled=True)
    
    st.divider()
    st.markdown("### ⚙️ Cara Penggunaan")
    st.markdown("""
    1. Upload file CV/Resume kandidat dalam format **PDF**.
    2. Klik tombol **Evaluate Candidate**.
    3. Tunggu AI menganalisis dan memberikan skor.
    """)
    
    st.divider()
    st.info("Sistem ini mengevaluasi berdasarkan Tech Stack, Pengalaman, Portofolio, dan Pendidikan secara objektif.")

# --- MAIN CONTENT (Area Utama) ---
st.title("💼 Candidate Evaluation Dashboard")
st.markdown("Streamline your technical hiring process with AI-driven resume analysis.")
st.write("") # Spasi kosong

# Membagi layar menjadi 2 kolom (Kiri 30%, Kanan 70%)
col1, col2 = st.columns([3, 7])

with col1:
    # Kotak Upload File
    with st.container(border=True):
        st.subheader("📥 Upload Resume")
        uploaded_file = st.file_uploader("Pilih file PDF", type=["pdf"], label_visibility="collapsed")
        
        if uploaded_file is not None:
            st.success(f"📄 {uploaded_file.name} siap dievaluasi.")
            
            # Tombol Evaluasi
            analyze_btn = st.button("Evaluate Candidate 🚀")

with col2:
    # Kotak Hasil Evaluasi
    with st.container(border=True):
        st.subheader("📊 Evaluation Report")
        
        if uploaded_file is None:
            st.info("👈 Silakan upload CV kandidat di panel sebelah kiri untuk melihat hasil evaluasi di sini.")
        
        elif uploaded_file is not None and analyze_btn:
            with st.spinner("Menganalisis profil kandidat secara mendalam..."):
                try:
                    # Menyiapkan file untuk dikirim
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    
                    # Mengirim request ke Backend
                    response = requests.post(BACKEND_URL, files=files)
                    
                    if response.status_code == 200:
                            data = response.json()
                            ai_text = data["ai_analysis"]
                            
                            # 1. FILTER PEMIKIRAN MODEL: Hapus semua teks di dalam tag <think> ... </think>
                            ai_text = re.sub(r'<think>.*?</think>', '', ai_text, flags=re.DOTALL)
                            
                            # 2. FILTER BASA-BASI: Memastikan teks HANYA mulai dari "**Candidate Name**"
                            if "**Candidate Name**" in ai_text:
                                clean_output = "**Candidate Name**" + ai_text.split("**Candidate Name**", 1)[1]
                            else:
                                clean_output = ai_text.strip()
                            
                            # Menampilkan hasil dengan animasi toast
                            st.toast('Evaluasi Selesai!', icon='✅')
                            
                            # Menampilkan teks Markdown hasil AI yang sudah bersih
                            st.markdown(clean_output)
                        
                    else:
                        st.error(f"Terjadi kesalahan server: {response.json().get('detail', 'Unknown error')}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("🚨 Gagal terhubung ke Backend. Pastikan server FastAPI sudah berjalan (uvicorn backend:app --reload)!")