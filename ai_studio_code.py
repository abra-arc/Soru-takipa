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
        ders TEXT,
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

# Sayfa
st.set_page_config(
    page_title="AI Soru Çözücü",
    page_icon="🧠",
    layout="centered"
)

sayfa = st.sidebar.selectbox(
    "Menü",
    ["Soru Çöz", "Soru Depom"]
)

# ==========================
# SORU ÇÖZ
# ==========================
if sayfa == "Soru Çöz":

    st.title("🧠 AI Soru Çözücü")

    st.markdown(
        "Sorunun fotoğrafını yükle. Yapay zeka soruyu analiz edip çözsün."
    )

    ders = st.selectbox(
        "📚 Ders Seç",
        [
            "Matematik",
            "Türkçe",
            "Fen Bilimleri",
            "Sosyal Bilgiler",
            "İngilizce",
            "Diğer"
        ]
    )

    uploaded_file = st.file_uploader(
        "📸 Soru Fotoğrafını Yükle",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file:

        image = Image.open(uploaded_file)

        st.image(
            image,
            caption="Yüklenen Soru",
            width=300
        )

        if st.button(
            "🚀 Soruyu Çöz",
            use_container_width=True,
            key="coz_button"
        ):

            with st.spinner("Sorun analiz ediliyor..."):

                prompt = """
                Bu görseldeki soruyu analiz et.

                Kurallar:
                - Soruyu çöz.
                - Adım adım açıkla.
                - Gereksiz konuşma yapma.
                """

                response = model.generate_content(
                    [prompt, image]
                )

                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()

                tarih = datetime.now().strftime(
                    "%d.%m.%Y %H:%M"
                )

                dosya_adi = f"{int(datetime.now().timestamp())}.png"
                dosya_yolu = os.path.join(
                    IMAGE_DIR,
                    dosya_adi
                )

                image.save(dosya_yolu)

                cursor.execute("""
                INSERT INTO sorular
                (ders, gorsel_yolu, cozum_metni, tarih)
                VALUES (?, ?, ?, ?)
                """,
                (
                    ders,
                    dosya_yolu,
                    response.text,
                    tarih
                ))

                conn.commit()
                conn.close()

                st.success("Çözüm hazır!")

                st.markdown("## 📦 Çözüm")
                st.write(response.text)

# ==========================
# SORU DEPOM
# ==========================
elif sayfa == "Soru Depom":

    st.title("📚 Soru Depom")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT ders, gorsel_yolu,
           cozum_metni, tarih
    FROM sorular
    ORDER BY id DESC
    """)

    sorular = cursor.fetchall()

    conn.close()

    if len(sorular) == 0:
        st.info("Henüz kayıtlı soru yok.")

    else:

        dersler = {}

        for soru in sorular:

            ders = soru[0]

            if ders not in dersler:
                dersler[ders] = []

            dersler[ders].append(soru)

        for ders_adi, liste in dersler.items():

            st.header(f"📂 {ders_adi}")

            for soru in liste:

                st.markdown("---")

                if os.path.exists(soru[1]):
                    st.image(
                        soru[1],
                        width=250
                    )

                st.write("### Çözüm")
                st.write(soru[2])

                st.caption(soru[3])
