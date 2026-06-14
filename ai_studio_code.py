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
    page_title="Akıllı Soru Asistanı",
    page_icon="🎓",
    layout="centered"
)
#uzay teması
st.markdown("""
<style>

/* Uzay Teması */
.stApp {
    background: linear-gradient(
        180deg,
        #020617 0%,
        #0f172a 50%,
        #1e1b4b 100%
    );
}

/* Yıldızlar */
.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;

    background-image:
        radial-gradient(white 1px, transparent 1px),
        radial-gradient(white 1px, transparent 1px),
        radial-gradient(#93c5fd 1px, transparent 1px);

    background-size:
        50px 50px,
        100px 100px,
        150px 150px;

    background-position:
        0 0,
        25px 25px,
        75px 75px;

    pointer-events: none;
    z-index: -1;
}

/* Başlıklar */
h1, h2, h3 {
    color: white !important;
    text-align: center;
}

/* Yazılar */
p, label, span {
    color: white !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.9);
}

/* Butonlar */
div.stButton > button {
    width: 100%;
    height: 55px;
    border-radius: 15px;

    background: linear-gradient(
        90deg,
        #2563eb,
        #7c3aed
    );

    color: white;
    font-size: 18px;
    font-weight: bold;
    border: none;
}

/* Buton Hover */
div.stButton > button:hover {
    transform: scale(1.03);
    transition: 0.2s;
}

/* Resimler */
[data-testid="stImage"] img {
    border-radius: 20px;
    border: 2px solid rgba(255,255,255,0.2);
}

</style>
""", unsafe_allow_html=True)

sayfa = st.sidebar.selectbox(
    "Menü",
    ["Soru Çöz", "Soru Depom"]
)

# ==========================
# SORU ÇÖZ
# ==========================
if sayfa == "Soru Çöz":

    st.title("Artık Sorun Yok")

    st.markdown(
        "Sorunun fotoğrafını yükle. Yapay zeka soruyu analiz edip çözsün."
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

Önce sorunun ait olduğu dersi veya alanı belirle.

Cevabı şu formatta ver:

DERS: [alan adı]

ÇÖZÜM:
[sorunun çözümü]

Ders adını mümkün olduğunca spesifik yaz.
Örneğin:
- Matematik
- Geometri
- Fizik
- Kimya
- KPSS Tarih
- KPSS Coğrafya
- İngilizce
- Programlama
- Elektrik Elektronik
- Muhasebe
- Hukuk

veya uygun gördüğün başka bir alan.

Başka açıklama yapma.
"""
                response = model.generate_content(
                    [prompt, image]
                )
                
            cevap = response.text

ders = "Diğer"

if "DERS:" in cevap:
    try:
        ders = cevap.split("DERS:")[1].split("\n")[0].strip()
    except:
        pass
        
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
