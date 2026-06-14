import streamlit as st
from PIL import Image
import google.generativeai as genai
import sqlite3
from datetime import datetime
import os

# AYARLAR

DB_FILE = "sorular.db"
IMAGE_DIR = "sorular"

os.makedirs(IMAGE_DIR, exist_ok=True)

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

# VERİTABANI

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

# SAYFA

st.set_page_config(
page_title="Nova AI",
page_icon="🌌",
layout="centered"
)


# TEMA

st.markdown("""

<style>

.stApp{
    background: linear-gradient(
        180deg,
        #020617,
        #0f172a,
        #1e1b4b
    );
}

h1,h2,h3,label,p,span{
    color:white !important;
}

[data-testid="stSidebar"]{
    background:rgba(15,23,42,0.95);
}

div.stButton > button{
    width:100%;
    border-radius:15px;
    height:55px;
    font-size:18px;
    font-weight:bold;
}

</style>

""", unsafe_allow_html=True)

#MENU

sayfa = st.sidebar.selectbox(
"Menü",
["Soru Çöz", "Soru Depom"]
)

#SORU ÇÖZ

if sayfa == "Soru Çöz":

    st.title("🌌 Nova AI")
    
    st.caption(
        "Sorunu yükle, yapay zeka çözsün."
    )

uploaded_file = st.file_uploader(
    "📸 Soru Yükle",
    type=["png","jpg","jpeg"]
)

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(
        image,
        width=250
    )

    if st.button(
        "🚀 Soruyu Çöz",
        use_container_width=True
    ):

        with st.spinner(
            "Sorun analiz ediliyor..."
        ):

            prompt = """

Bu görseldeki soruyu çöz.

Önce dersi belirle.

Şu formatta cevap ver:

DERS: ...

ÇÖZÜM:
...

Başka açıklama yapma.
"""
            
            response = model.generate_content(
                [prompt, image]
            )

            cevap = response.text

            ders = "Diğer"

            if "DERS:" in cevap:
                try:
                    ders = cevap.split(
                        "DERS:"
                    )[1].split(
                        "\n"
                    )[0].strip()
                except:
                    pass

            tarih = datetime.now().strftime(
                "%d.%m.%Y %H:%M"
            )

            dosya_adi = (
                f"{int(datetime.now().timestamp())}.png"
            )

            dosya_yolu = os.path.join(
                IMAGE_DIR,
                dosya_adi
            )

            image.save(dosya_yolu)

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO sorular
            (
                ders,
                gorsel_yolu,
                cozum_metni,
                tarih
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                ders,
                dosya_yolu,
                cevap,
                tarih
            ))

            conn.commit()
            conn.close()

            st.success("Çözüm hazır!")

            if "ÇÖZÜM:" in cevap:
                st.write(
                    cevap.split(
                        "ÇÖZÜM:"
                    )[1]
                )
            else:
                st.write(cevap)


# SORU DEPOM

elif sayfa == "Soru Depom":

    st.title("📚 Soru Depom")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT ders,
           gorsel_yolu,
           cozum_metni,
           tarih
    FROM sorular
    ORDER BY id DESC
    """)
    
    sorular = cursor.fetchall()
    
    conn.close()

if not sorular:

    st.info(
        "Henüz kayıtlı soru yok."
    )

else:

    dersler = {}

    for soru in sorular:

        ders = soru[0]

        if ders not in dersler:
            dersler[ders] = []

        dersler[ders].append(soru)

    for ders_adi, liste in dersler.items():

        with st.expander(
            f"📂 {ders_adi} ({len(liste)})"
        ):

            for soru in liste:

                if os.path.exists(
                    soru[1]
                ):
                    st.image(
                        soru[1],
                        width=200
                    )

                st.write(
                    soru[2]
                )

                st.caption(
                    soru[3]
                )

                st.markdown("---")
