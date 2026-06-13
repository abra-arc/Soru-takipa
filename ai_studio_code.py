import streamlit as st
from PIL import Image
import google.generativeai as genai
import sqlite3
from datetime import datetime
import os 
DB_FILE = "sorular.db"
IMAGE_DIR = "sorular"

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sorular (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gorsel_yolu TEXT,
        cozum_metni TEXT,
        tarih TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

# Sayfa ayarları
st.set_page_config(
    page_title="AI Soru Çözücü",
    page_icon="🧠",
    layout="centered"
)

# Başlık
st.title("🧠 AI Soru Çözücü")
st.markdown(
    "Sorunun fotoğrafını yükle. Yapay zeka soruyu analiz edip çözsün."
)

# Dosya yükleme
uploaded_file = st.file_uploader(
    "📸 Soru Fotoğrafını Yükle",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(
        image,
        caption="Yüklenen Soru",
        use_container_width=True
    )

    if st.button("🚀 Soruyu Çöz", use_container_width=True):

        with st.spinner("Sorun analiz ediliyor..."):

            prompt = """
            Bu görseldeki soruyu analiz et.

            Kurallar:
            soruyu çöz başka hiçbirşey söyleme
            
            """

            response = model.generate_content(
                [prompt, image]
            )

            st.success("Çözüm hazır!")

            st.markdown("## 📚 Çözüm")

            st.write(response.text)
