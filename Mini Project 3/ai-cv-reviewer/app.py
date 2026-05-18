import streamlit as st
import requests

# Konfigurasi Endpoint Backend
BACKEND_URL = "http://localhost:8000/analyze-cv/"

st.set_page_config(page_title="AI CV Reviewer", page_icon="📄", layout="wide")

st.title("📄 AI CV/Resume Reviewer")
st.markdown("""
Aplikasi ini dibuat khusus untuk mengevaluasi kandidat **AI Engineer**. 
Sistem akan mengekstrak CV dan menggunakan *Gemini AI* untuk memberikan penilaian mendalam berdasarkan *Python*, *Machine Learning*, dan *Generative AI*.
""")

st.divider()

# Komponen File Upload
uploaded_file = st.file_uploader("Upload CV Kandidat (Hanya format PDF, Maks. 5MB)", type=["pdf"])

if uploaded_file is not None:
    # Pra-validasi ukuran di sisi Frontend
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > 5:
        st.error(f"⚠️ Ukuran file terlalu besar! Ukuran file: {file_size_mb:.2f}MB. Maksimal 5MB.")
    else:
        st.success(f"File '{uploaded_file.name}' siap untuk dianalisis.")
        
        if st.button("🚀 Analisis CV Sekarang", type="primary", use_container_width=True):
            with st.spinner("Mengirim dokumen ke server dan sedang dianalisis oleh AI... (Biasanya memakan waktu 10-20 detik)"):
                try:
                    # Menyiapkan payload untuk dikirim ke FastAPI
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    
                    # POST request ke Backend
                    response = requests.post(BACKEND_URL, files=files, timeout=60)
                    
                    if response.status_code == 200:
                        evaluation_result = response.json().get("evaluation", "")
                        
                        st.divider()
                        st.subheader("📊 Hasil Evaluasi Kandidat")
                        # Merender output Markdown langsung dari Gemini AI
                        st.markdown(evaluation_result)
                    else:
                        st.error(f"Error {response.status_code}: {response.json().get('detail', 'Unknown error')}")
                
                except requests.exceptions.ConnectionError:
                    st.error("Gagal terhubung ke backend server. Pastikan FastAPI sudah berjalan di http://localhost:8000.")
                except requests.exceptions.Timeout:
                    st.error("Request Timeout. AI membutuhkan waktu lebih lama dari biasanya untuk merespon.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")