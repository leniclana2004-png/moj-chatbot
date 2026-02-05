# app.py - Chatbot VRTNAR SPECIALIST

# 1. UVOZ POTREBNIH KNJIŽNIC
import streamlit as st
from groq import Groq
import os
from datetime import datetime

# 2. NASTAVITEV STRANI
st.set_page_config(
    page_title="🌿 Moj Vrtnarski Pomagalec",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 3. FUNKCIJA ZA INICIALIZACIJO POGOVORA
def inicializiraj_pogovor():
    """Inicializira session state za shranjevanje pogovora"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

# 4. FUNKCIJA ZA DOBIVANJE GROQ KLIENTA
def get_groq_client():
    """Ustvari in vrne Groq klienta z API ključem"""
    try:
        # Poskusi dobiti ključ iz Streamlit Secrets
        api_key = st.secrets["GROQ_API_KEY"]
    except:
        try:
            # Za lokalno okolje
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("GROQ_API_KEY")
        except:
            st.error("❌ API ključ ni bil najden! Dodaj ga v .env datoteko.")
            st.info("""
            **Navodila za .env datoteko:**
            1. V mapi CHATBOT odpri datoteko `.env` (ali ustvari novo)
            2. Vpiši: `GROQ_API_KEY="tvoj-groq-api-ključ-tukaj"`
            3. Shrani datoteko
            """)
            return None
    
    return Groq(api_key=api_key)

# 5. SISTEMNO SPOROČILO ZA VRTNARSKO SPECIALIZACIJO
def get_system_message():
    """Vrne sistemsko sporočilo, ki določa specializacijo chatbota"""
    
    specializacija = """Ti si VRTNAR SPECIALIST - strokovnjak za vrtnarjenje in rastlinstvo.

🌿 **Tvoja specializacija (SAMO te teme):**
1. 🌱 VZGOJA RASTLIN (zelenjave, rož, dreves, zelišč)
2. 🏡 VRSTI VRTOV (čebulnični, zeliščni, zelenjavni, okrasni)
3. 📅 SEZONSKA VRTNARJENJA (spomladanska, poletna, jesenska, zimska)
4. 🌧️ NEGA RASTLIN (zalivanje, gnojenje, obrezovanje)
5. 🐛 BOLESNI IN ŠKODLJIVCI (prepoznavanje in zdravljenje)
6. 🌍 ZEMLJA IN SUBSTRATI (vrste tal, izboljšave)
7. 🪴 SOBAŃKE RASTLINE in njihova nega
8. ♻️ EKOLOŠKO VRTNARJENJE (kompostiranje, naravni škodljivci)
9. 💧 NAVADILNI SISTEMI in varčevanje z vodo
10. 🌞 LEGA VRTA (sončna/senčna mesta)

🚫 **TEME IZVEN SPECIALIZACIJE (NE odgovarjaj):**
- Politika, novosti, aktualni dogodki
- Kuhinja, recepti, kulinarika
- Šport, zabava, celebrity
- Tehnologija, računalništvo
- Avtomobili, mehanika
- Finance, gospodarstvo
- Zdravstvo, medicina (razen rastlinskih bolezni)
- Vse ostalo, kar ni direktno povezano z vrtnarjenjem

📝 **PRAVILA ZA ODGOVARJANJE:**
1. Odgovarjaj IZKLJUČNO V SLOVENŠČINI!
2. Odgovori morajo biti praktični, natančni in koristni
3. Vključi konkretne podatke (temperature, čase, mere)
4. Za vsako rastlinsko vrsto navedi posebne potrebe
5. Upoštevaj slovenske podnebne razmere
6. Če ne veš, priznaj in predlagaj, kje najti informacije
7. Vedno ohranjaj prijazen, profesionalen ton
8. Za vprašanja izven specializacije VLJUJNO ZAVRNI

🎯 **PRIMERI ZAVRNITVE:**
- "Oprostite, ampak moja specializacija je samo vrtnarjenje in rastlinstvo. Za vprašanja o [tema] vam ne morem pomagati."
- "Kot vrtnarski specialist se osredotočam samo na rastline in vrtove. Vprašanje o [tema] žal ne spada v moj strokovni krog."
- "Na žalost sem omejen na vrtnarska vprašanja. Za informacije o [tema] boste potrebovali druge vire."

🌼 **FORMAT ODGOVOROV:**
- Uporabi jasne korake in naslove
- Za pomembne informacije uporabi **krepko pisavo**
- Za sezone uporabi 📅 emojije
- Za težavnost uporabi ⭐ zvezdice
- Za tabele uporabi Markdown formate

⚠️ **POMEMBNO:** Nikoli ne odgovarjaj na vprašanja, ki niso o vrtnarjenju! Vedno ostani znotraj svoje specializacije."""
    
    return {"role": "system", "content": specializacija}

# 6. FUNKCIJA ZA GENERIRANJE ODGOVORA
def generiraj_odgovor(client, uporabnisko_vprasanje):
    """Pokliče Groq API in generira odgovor"""
    
    # Pripravi seznam sporočil za AI
    sporocila_za_ai = [get_system_message()]
    
    # Dodaj zgodovino (zadnjih 10 sporočil za kontekst)
    for sporocilo in st.session_state.chat_history[-10:]:
        sporocila_za_ai.append(sporocilo)
    
    # Dodaj trenutno vprašanje
    sporocila_za_ai.append({"role": "user", "content": uporabnisko_vprasanje})
    
    try:
        # Pokliči Groq API
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=sporocila_za_ai,
            temperature=0.7,
            max_tokens=1200,
            top_p=0.9
        )
        
        # Pridobi odgovor
        odgovor = completion.choices[0].message.content
        
        # Shrani v zgodovino
        st.session_state.chat_history.append({"role": "user", "content": uporabnisko_vprasanje})
        st.session_state.chat_history.append({"role": "assistant", "content": odgovor})
        
        return odgovor
        
    except Exception as e:
        return f"❌ Napaka pri komunikaciji z AI: {str(e)}\n\nPoskusite znova."

# 7. FUNKCIJA ZA PRIKAZ ZGODOVINE
def prikazi_zgodovino():
    """Prikaže celotno zgodovino pogovora"""
    for sporocilo in st.session_state.messages:
        with st.chat_message(sporocilo["role"]):
            st.markdown(sporocilo["content"])

# 8. GLAVNA FUNKCIJA
def main():
    """Glavna funkcija aplikacije"""
    
    # Inicializiraj pogovor
    inicializiraj_pogovor()
    
    # Pridobi Groq klienta
    client = get_groq_client()
    
    # CSS za lepši izgled
    st.markdown("""
    <style>
    .stChatMessage {
        border-radius: 10px;
        margin: 8px 0;
        padding: 12px;
    }
    .css-1d391kg {
        background-color: #f8fff8;
    }
    .stButton button {
        background-color: #2e7d32;
        color: white;
        border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # SIDEBAR
    with st.sidebar:
        st.title("🌿 Vrtnarski Pomagalec")
        st.divider()
        
        # Sezonski nasveti
        with st.expander("📅 Sezonski nasveti", expanded=False):
            current_month = datetime.now().month
            if 3 <= current_month <= 5:
                st.write("**SPOMLAD:** Sadite čebulice, obrezujte grmovnice")
            elif 6 <= current_month <= 8:
                st.write("**POLETJE:** Redno zalivajte, ščitite pred vročino")
            elif 9 <= current_month <= 11:
                st.write("**JESEN:** Pospravite vrt, sajte jesenske rastline")
            else:
                st.write("**ZIMA:** Pripravite na pomlad, zaščitite pred mrazom")
        
        st.divider()
        
        st.subheader("ℹ️ O chatbota")
        st.write("""
        **Specializacija:** Vrtnarjenje in rastlinstvo  
        **Jezik:** Slovenščina  
        **Področja:** Zelenjava, rože, drevesa, zelišča  
        
        🌱 Ohranja kontekst trenutnega pogovora  
        🔄 Ponastavi se ob osvežitvi strani
        """)
        
        st.divider()
        
        # Hitri nasveti
        st.subheader("💡 Hitri nasveti")
        tips = [
            "🌅 Rastline zalivaj zjutraj ali zvečer",
            "🌧️ Prekomerno zalivanje škoduje koreninam",
            "🪲 Naravni škodljivci: polži, uši, gosenice",
            "♻️ Kompost je najboljši gnojilo",
            "🌞 Poznaj potrebe rastlin po svetlobi"
        ]
        for tip in tips:
            st.write(f"- {tip}")
        
        st.divider()
        
        # Gumbi za upravljanje
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Ponastavi", use_container_width=True):
                st.session_state.messages = []
                st.session_state.chat_history = []
                st.rerun()
        
        with col2:
            if st.button("💾 Kopiraj", use_container_width=True):
                st.info("Pogovor se samodejno shrani v seji")
        
        # Števec
        st.divider()
        st.write(f"💬 Sporočil v pogovoru: **{len(st.session_state.messages)}**")
        st.caption("Model: Mixtral 8x7B | 🌿 Specializacija: Vrtnarjenje")
    
    # GLAVNO OBMOČJE
    st.title("🌱 Dobrodošli v Svetu Vrtnarjenja!")
    
    # Uvodno sporočilo
    with st.expander("🎯 Kaj lahko vprašate?", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🌿 Začetniki:**
            - Kako začeti z vrtom?
            - Katere rastline so najlažje?
            - Kaj potrebujem za začetek?
            """)
        
        with col2:
            st.markdown("""
            **🪴 Nega rastlin:**
            - Kako zalivati?
            - Kdaj gnojiti?
            - Kako prepoznati bolezni?
            """)
        
        with col3:
            st.markdown("""
            **📅 Sezonsko:**
            - Kaj saditi spomladi?
            - Kako pripraviti vrt na zimo?
            - Katere rože cvetijo poleti?
            """)
    
    st.divider()
    
    # Hitri vprašanja
    st.subheader("🚀 Hitra vprašanja")
    quick_questions = st.columns(4)
    
    with quick_questions[0]:
        if st.button("🌹 Rože", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Katere rože so najboljše za začetnike?"})
            st.rerun()
    
    with quick_questions[1]:
        if st.button("🥕 Zelenjava", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Katero zelenjavo lahko sadim spomladi?"})
            st.rerun()
    
    with quick_questions[2]:
        if st.button("🌳 Drevesa", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Kdaj je najboljši čas za sajenje dreves?"})
            st.rerun()
    
    with quick_questions[3]:
        if st.button("🪴 Sobanke", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Katere sobanske rastline so najbolj okrepčujoče?"})
            st.rerun()
    
    st.divider()
    
    # Prikaz pogovora
    st.subheader("💬 Pogovor")
    prikazi_zgodovino()
    
    # Vnosno polje
    if vprasanje := st.chat_input("Vpišite vaše vrtnarsko vprašanje...", key="chat_input"):
        # Preveri klienta
        if client is None:
            st.error("Napaka: Groq klient ni inicializiran.")
            return
        
        # Prikaži uporabniško sporočilo
        with st.chat_message("user"):
            st.markdown(vprasanje)
        
        # Shrani za prikaz
        st.session_state.messages.append({"role": "user", "content": vprasanje})
        
        # Generiraj odgovor
        with st.chat_message("assistant", avatar="🌿"):
            with st.spinner("🌱 Razmišljam o odgovoru..."):
                odgovor = generiraj_odgovor(client, vprasanje)
                
                # Formatiran odgovor
                st.markdown(odgovor)
                
                # Dodaj emojije glede na vsebino
                if "zalivanje" in vprasanje.lower():
                    st.caption("💧 Pomembno: Prekomerno zalivanje je pogosta napaka!")
                elif "gnojenje" in vprasanje.lower():
                    st.caption("🌱 Nasvet: Uporabi naravna gnojila za boljše rezultate!")
        
        # Shrani odgovor
        st.session_state.messages.append({"role": "assistant", "content": odgovor})
        
        # Samodejno se pomakni navzdol
        st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)

# 9. ZAŽENI APLIKACIJO
if __name__ == "__main__":
    main()