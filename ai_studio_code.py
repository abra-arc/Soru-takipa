import streamlit as st
import sqlite3
import os
from datetime import datetime
from PIL import Image

import streamlit as st    
import sqlite3
import os
from datetime import datetime
from PIL import Image

import google.generativeai as genai

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

# Veritabanı ve klasör kurulumları
DB_FILE = "ders_takip.db"  
IMAGE_DIR = "yuklenen_sorular"

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

def init_db():
    """Veritabanı tablolarını oluşturur."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sorular (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gorsel_yolu TEXT,
            ders TEXT,
            konu TEXT,
            cozum_metni TEXT,
            durum TEXT, -- 'Anlaşıldı' veya 'Tekrar Edilmeli'
            tarih TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Yardımcı Fonksiyonlar
def soru_ekle(gorsel_yolu, ders, konu, cozum, durum):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    tarih_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute('''
        INSERT INTO sorular (gorsel_yolu, ders, konu, cozum_metni, durum, tarih)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (gorsel_yolu, ders, konu, cozum, durum, tarih_str))
    conn.commit()
    conn.close()

def sorulari_getir():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sorular ORDER BY id DESC")
    veriler = cursor.fetchall()
    conn.close()
    return veriler

def durum_guncelle(soru_id, yeni_durum):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE sorular SET durum = ? WHERE id = ?", (yeni_durum, soru_id))
    conn.commit()
    conn.close()

def soru_sil(soru_id, gorsel_yolu):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sorular WHERE id = ?", (soru_id,))
    conn.commit()
    conn.close()
    if os.path.exists(gorsel_yolu):
        os.remove(gorsel_yolu)

# Yapay Zeka Çözüm Simülasyonu
# (Burayı isteğe bağlı olarak OpenAI veya Google Gemini API ile entegre edebilirsiniz)
def yapay_zeka_cozum_uret(ders, konu):
    prompt = f"""
    Ders: {ders}
    Konu: {konu}

    Bu konu için öğrencinin anlayabileceği şekilde detaylı çözüm ve açıklama yap.
    """

    response = model.generate_content(prompt)
    return response.text
    
# Streamlit Arayüzü
st.set_page_config(page_title="Ders ve Soru Takip Platformu", layout="wide")

st.sidebar.title("Menü")
sayfa = st.sidebar.radio("Gitmek istediğiniz sayfa:", ["Soru Yükle ve Çöz", "Soru Depom", "Konu Eksikleri Analizi"])

# --- SAYFA 1: SORU YÜKLE VE ÇÖZ ---
if sayfa == "Soru Yükle ve Çöz":
    st.title("📚 Yeni Soru Yükle ve Çözüm Al")
    st.write("Sorunuzun fotoğrafını yükleyin, ders ve konu bilgilerini girerek çözüm adımlarını oluşturun.")

    uploaded_file = st.file_uploader("Soru Fotoğrafı Seçin", type=["png", "jpg", "jpeg"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        ders = st.selectbox("Ders", ["Matematik", "Fizik", "Kimya", "Biyoloji", "Türkçe", "Tarih", "Coğrafya"])
        konu = st.text_input("Konu Başlığı (Örn: Türev, Optik, Mol Kavramı vb.)")
        durum = st.selectbox("Başlangıç Durumu", ["Tekrar Edilmeli", "Anlaşıldı"])

    if uploaded_file is not None and konu != "":
        # Görseli göster
        image = Image.open(uploaded_file)
        st.image(image, caption="Yüklenen Soru", use_container_width=True)
        
        if st.button("Soruyu Çöz ve Kaydet"):
            # Görseli yerel klasöre kaydet
            dosya_adi = f"{int(datetime.now().timestamp())}_{uploaded_file.name}"
            kayit_yolu = os.path.join(IMAGE_DIR, dosya_adi)
            image.save(kayit_yolu)
            
            # Çözüm üret (Şimdilik simüle edilmiş yapay zeka)
            cozum = yapay_zeka_cozum_uret(ders, konu)
            
            # Veritabanına kaydet
            soru_ekle(kayit_yolu, ders, konu, cozum, durum)
            st.success("Soru başarıyla kaydedildi ve analiz edildi!")
            
            st.subheader("Üretilen Çözüm:")
            st.info(cozum)

# --- SAYFA 2: SORU DEPOSU ---
elif sayfa == "Soru Depom":
    st.title("🗂️ Soru Depom")
    st.write("Daha önce yüklediğiniz soruları listeleyebilir, durumlarını güncelleyebilir veya silebilirsiniz.")

    sorular = sorulari_getir()
    
    if not sorular:
        st.info("Henüz yüklenmiş bir soru bulunmuyor.")
    else:
        ders_filtresi = st.multiselect("Ders Filtrele", list(set([s[2] for s in sorular])))
        durum_filtresi = st.multiselect("Durum Filtrele", ["Anlaşıldı", "Tekrar Edilmeli"])
        
        for soru in sorular:
            s_id, gorsel_yolu, s_ders, s_konu, s_cozum, s_durum, s_tarih = soru
            
            # Filtreleme mantığı
            if ders_filtresi and s_ders not in ders_filtresi:
                continue
            if durum_filtresi and s_durum not in durum_filtresi:
                continue
                
            with st.container():
                st.markdown("---")
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if os.path.exists(gorsel_yolu):
                        st.image(Image.open(gorsel_yolu), use_container_width=True)
                    else:
                        st.warning("Görsel dosyası bulunamadı.")
                
                with col2:
                    st.subheader(f"{s_ders} - {s_konu}")
                    st.caption(f"Yükleme Tarihi: {s_tarih}")
                    
                    st.write("**Çözüm:**")
                    st.text(s_cozum)
                    
                    st.write(f"**Güncel Durum:** {s_durum}")
                    
                    # Durum değiştirme ve silme butonları
                    sub_col1, sub_col2 = st.columns(2)
                    with sub_col1:
                        yeni_durum = st.selectbox(
                            "Durumu Değiştir", 
                            ["Anlaşıldı", "Tekrar Edilmeli"], 
                            index=0 if s_durum == "Anlaşıldı" else 1,
                            key=f"status_{s_id}"
                        )
                        if yeni_durum != s_durum:
                            durum_guncelle(s_id, yeni_durum)
                            st.rerun()
                            
                    with sub_col2:
                        if st.button("Soruyu Sil", key=f"delete_{s_id}", type="secondary"):
                            soru_sil(s_id, gorsel_yolu)
                            st.rerun()

# --- SAYFA 3: KONU EKSİKLERİ ANALİZİ ---
elif sayfa == "Konu Eksikleri Analizi":
    st.title("📊 Gelişim ve Konu Eksikleri")
    st.write("Hangi konularda daha fazla yardıma veya tekrara ihtiyacınız olduğunu buradan takip edebilirsiniz.")

    sorular = sorulari_getir()
    
    if not sorular:
        st.info("Eksik analizi yapabilmek için önce birkaç soru yüklemelisiniz.")
    else:
        # Konu bazlı analiz yapma
        eksik_konular = {}
        toplam_sorular = {}
        
        for soru in sorular:
            _, _, s_ders, s_konu, _, s_durum, _ = soru
            anahtar = f"{s_ders} -> {s_konu}"
            
            toplam_sorular[anahtar] = toplam_sorular.get(anahtar, 0) + 1
            if s_durum == "Tekrar Edilmeli":
                eksik_konular[anahtar] = eksik_konular.get(anahtar, 0) + 1

        # Metrikler
        toplam_kayit = len(sorular)
        tekrar_gereken = sum(1 for s in sorular if s[5] == "Tekrar Edilmeli")
        anlasilan = toplam_kayit - tekrar_gereken
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Toplam Soru", toplam_kayit)
        col2.metric("Anlaşılan Soru", anlasilan)
        col3.metric("Tekrar Edilecek Soru", tekrar_gereken)
        
        st.subheader("⚠️ Acil Tekrar Edilmesi Gereken Konular")
        st.write("Aşağıdaki konular, 'Tekrar Edilmeli' olarak işaretlediğiniz çözemediğiniz soruları içermektedir:")
        
        if not eksik_konular:
            st.success("Tüm soruları 'Anlaşıldı' olarak işaretlediniz. Harika gidiyorsunuz! 🎉")
        else:
            for konu_adi, adet in eksik_konular.items():
                oran = (adet / toplam_sorular[konu_adi]) * 100
                st.warning(f"**{konu_adi}**: Bu konudan {toplam_sorular[konu_adi]} sorunun {adet} tanesi henüz anlaşılamadı.")
                st.progress(oran / 100.0)
