import streamlit as st
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from datetime import date, timedelta

# --- GRUNDKONFIGURATION -----------------------------------------------------

# App-Konfiguration für eine breitere Ansicht
st.set_page_config(
    page_title="Widerspruchs-Assistent Pflegegrad",
    page_icon="⚖️",
    layout="wide"
)

# Lade API-Key sicher (funktioniert lokal und auf dem Server)
try:
    MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]
except (KeyError, FileNotFoundError):
    MISTRAL_API_KEY = "UZtiS57vajTq0Gj9kJbQGJeVldLxV6Bn" # Für lokale Entwicklung

# Definiere die Prozessschritte
PROZESS_SCHRITTE = [
    "1. Start & Fristberechnung",
    "2. Dokumente sammeln",
    "3. Widerspruch formulieren",
    "4. Abschluss & Versand"
]

# Initialisiere den "Session State", um Daten über Interaktionen hinweg zu speichern
if 'prozess_schritt' not in st.session_state:
    st.session_state.prozess_schritt = 0
if 'bescheid_datum' not in st.session_state:
    st.session_state.bescheid_datum = None
if 'frist_ende' not in st.session_state:
    st.session_state.frist_ende = None
if 'hochgeladene_dateien' not in st.session_state:
    st.session_state.hochgeladene_dateien = []
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- SEITENLEISTE (Sidebar) für Navigation & Fortschritt --------------------

with st.sidebar:
    st.title("Navigation")
    st.write("Ihr Fortschritt im Widerspruchsprozess.")

    # **FEATURE: FORTSCHRITTSBALKEN**
    # Berechnet den Fortschritt in Prozent
    fortschritt_prozent = int((st.session_state.prozess_schritt / (len(PROZESS_SCHRITTE) - 1)) * 100)
    st.progress(fortschritt_prozent)
    
    # Zeigt den aktuellen Schritt an
    st.markdown(f"**Aktueller Schritt:**")
    st.info(f"{PROZESS_SCHRITTE[st.session_state.prozess_schritt]}")
    st.markdown("---")

    # **FEATURE: KALENDER MIT FRISTEN**
    st.subheader("Ihre Fristen")
    if st.session_state.frist_ende:
        st.date_input(
            "Widerspruchsfrist endet am:",
            value=st.session_state.frist_ende,
            disabled=True # Nur zur Anzeige, nicht änderbar
        )
        tage_verbleibend = (st.session_state.frist_ende - date.today()).days
        if tage_verbleibend >= 0:
            st.success(f"Sie haben noch {tage_verbleibend} Tage Zeit.")
        else:
            st.error("Die Frist ist bereits abgelaufen!")
    else:
        st.write("Noch keine Frist berechnet.")

    st.markdown("---")
    st.warning("Dieser Assistent ersetzt keine Rechtsberatung.")

# --- HAUPTBEREICH mit den einzelnen Prozessschritten ----------------------

st.title("Widerspruchs-Assistent Pflegegrad")

# === SCHRITT 1: START & FRISTBERECHNUNG =====================================
if st.session_state.prozess_schritt == 0:
    st.header(PROZESS_SCHRITTE[0])
    st.write("Bitte geben Sie das Datum ein, das auf Ihrem Pflegegrad-Bescheid steht. Daraus berechnen wir die gesetzliche Widerspruchsfrist.")

    bescheid_datum_input = st.date_input("Datum des Bescheids", value=st.session_state.get('bescheid_datum', date.today()))

    if st.button("Frist berechnen und Prozess starten"):
        st.session_state.bescheid_datum = bescheid_datum_input
        # Berechnung der Frist (vereinfacht: 1 Monat + 3 Tage Zustellfiktion)
        zugangs_datum = st.session_state.bescheid_datum + timedelta(days=3)
        # Bessere Monatsberechnung (z.B. 15. März -> 15. April)
        try:
            frist_monat = zugangs_datum.month % 12 + 1
            frist_jahr = zugangs_datum.year + (1 if zugangs_datum.month == 12 else 0)
            st.session_state.frist_ende = zugangs_datum.replace(month=frist_monat, year=frist_jahr)
        except ValueError: # Bei Monatsenden wie 31.
            st.session_state.frist_ende = zugangs_datum.replace(month=frist_monat, day=1, year=frist_jahr) - timedelta(days=1)
        
        st.session_state.prozess_schritt = 1
        st.rerun() # App neu laden, um zum nächsten Schritt zu springen

# === SCHRITT 2: DOKUMENTE SAMMELN ==========================================
elif st.session_state.prozess_schritt == 1:
    st.header(PROZESS_SCHRITTE[1])
    st.write("Laden Sie hier alle relevanten Dokumente hoch. Wichtig sind vor allem der **Pflegegrad-Bescheid** und das **MD-Gutachten**.")

    # **FEATURE: DATEI-UPLOAD**
    uploaded_files = st.file_uploader(
        "Dokumente hochladen (PDF, JPG, PNG)",
        type=["pdf", "jpg", "png", "jpeg"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.session_state.hochgeladene_dateien = uploaded_files
        st.success(f"{len(uploaded_files)} Datei(en) erfolgreich zur Kenntnis genommen.")
        for file in uploaded_files:
            st.write(f"- {file.name} ({round(file.size/1024)} KB)")

    if st.button("Weiter zum Widerspruchstext"):
        st.session_state.prozess_schritt = 2
        st.rerun()

# === SCHRITT 3: WIDERSPRUCH FORMULIEREN (Dein Chatbot) ======================
elif st.session_state.prozess_schritt == 2:
    st.header(PROZESS_SCHRITTE[2])
    st.write("Nutzen Sie den KI-Assistenten, um Ihren Widerspruch zu formulieren. Beschreiben Sie, was Ihrer Meinung nach falsch bewertet wurde.")
    
    # Der Chatbot-Code, den du bereits kennst
    for message in st.session_state.messages:
        with st.chat_message(message.role):
            st.markdown(message.content)

    if user_prompt := st.chat_input("Beschreiben Sie Ihr Anliegen..."):
        st.session_state.messages.append(ChatMessage(role="user", content=user_prompt))
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                client = MistralClient(api_key=MISTRAL_API_KEY)
                system_prompt = ChatMessage(
                    role="system",
                    content=(
                        "Du bist ein Experte für Pflegegrad-Widersprüche. Hilf dem Nutzer, einen sachlichen und gut begründeten Widerspruchstext zu formulieren. "
                        "Frage gezielt nach, welche Punkte aus dem MD-Gutachten strittig sind (z.B. Mobilität, Anziehen, Essen). "
                        "Gib konkrete Formulierungsvorschläge. Deine Rolle ist es, den Nutzer zu befähigen, seinen Fall klar darzulegen."
                    )
                )
                messages_for_api = [system_prompt] + st.session_state.messages
                
                chat_response = client.chat(model="mistral-small-latest", messages=messages_for_api)
                full_response = chat_response.choices[0].message.content
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                full_response = "Entschuldigung, es ist ein technischer Fehler aufgetreten."
                st.error(e)

            st.session_state.messages.append(ChatMessage(role="assistant", content=full_response))

    if st.button("Widerspruch ist fertig, weiter zum Abschluss"):
        st.session_state.prozess_schritt = 3
        st.rerun()

# === SCHRITT 4: ABSCHLUSS & VERSAND ========================================
elif st.session_state.prozess_schritt == 3:
    st.header(PROZESS_SCHRITTE[3])
    st.balloons()
    st.success("Herzlichen Glückwunsch, Sie haben fast alle Schritte abgeschlossen!")
    st.write("Hier ist eine Zusammenfassung Ihrer Daten:")

    st.subheader("Eingegebene Daten")
    st.write(f"- Datum des Bescheids: {st.session_state.bescheid_datum.strftime('%d.%m.%Y')}")
    st.write(f"- Widerspruchsfrist endet am: {st.session_state.frist_ende.strftime('%d.%m.%Y')}")

    st.subheader("Hochgeladene Dokumente")
    if st.session_state.hochgeladene_dateien:
        for file in st.session_state.hochgeladene_dateien:
            st.write(f"- {file.name}")
    else:
        st.write("Keine Dokumente hochgeladen.")

    st.subheader("Ihr Widerspruchstext (Auszug)")
    # Zeigt den letzten vom Nutzer eingegebenen Text als Beispiel
    user_messages = [m.content for m in st.session_state.messages if m.role == 'user']
    if user_messages:
        st.text_area("Ihr Text:", value=user_messages[-1], height=200, disabled=True)

    st.warning(
        "**Nächste Schritte:** Senden Sie den von Ihnen formulierten Widerspruch **unterschrieben per Einschreiben** an Ihre Pflegekasse. "
        "Halten Sie unbedingt die Frist ein!"
    )
    
    if st.button("Prozess neu starten"):
        # Setzt alles zurück
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
