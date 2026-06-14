import streamlit as st
from PIL import Image
import google.generativeai as genai
import sqlite3
from datetime import datetime
import os 
DB_FILE = "sorular.db"
IMAGE_DIR = "sorular"

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)
    
def init_db():
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

sayfa = st.sidebar.selectbox(
    "Menü",
    ["Soru Çöz", "Soru Depom"]
)

# Başlık
if sayfa == "Soru Çöz":
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

dosya_adi = f"{int(datetime.now().timestamp())}.png"
dosya_yolu = os.path.join(IMAGE_DIR, dosya_adi)

if st.button("🚀 Soruyu Çöz", use_container_width=True):
    with st.spinner("Sorun analiz ediliyor..."):
        
        response = model.generate_content(
            [prompt, image]
        )

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        tarih = datetime.now().strftime("%d.%m.%Y %H:%M")

        dosya_adi = f"{int(datetime.now().timestamp())}.png"
        dosya_yolu = os.path.join(IMAGE_DIR, dosya_adi)

        image.save(dosya_yolu)

        cursor.execute("""
        INSERT INTO sorular (gorsel_yolu, cozum_metni, tarih)
        VALUES (?, ?, ?)
        """, (dosya_yolu, response.text, tarih))
        
        conn.commit()
        conn.close()

        st.success("Çözüm hazır!")
        st.markdown("## 📦 Çözüm")
        st.write(response.text)

elif sayfa == "Soru Depom":
    st.title("📚 Soru Depom")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sorular ORDER BY id DESC")
    sorular = cursor.fetchall()

    conn.close()

    if len(sorular) == 0:
        st.info("Henüz kayıtlı soru yok.")
    else:
        for soru in sorular:
            st.markdown("---")

            if os.path.exists(soru[1]):
                st.image(soru[1], width=250)

            st.write("### Çözüm")
            st.write(soru[2])

            st.caption(soru[3])
