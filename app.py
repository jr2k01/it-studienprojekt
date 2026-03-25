import streamlit as st
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from datetime import date, timedelta
import base64 # Wird für die Anzeige von Dokumenten-Inhalten benötigt

# --- GRUNDKONFIGURATION -----------------------------------------------------

st.set_page_config(
    page_title="Widerspruchs-Assistent Pflegegrad",
    page_icon="⚖️",
    layout="wide"
)

# Lade API-Key sicher
try:
    MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]
except (KeyError, FileNotFoundError):
    MISTRAL_API_KEY = "DEIN_LOKALER_API_SCHLÜSSEL_HIER"

# --- INITIALISIERUNG DES SESSION STATE --------------------------------------
# Hier speichern wir alle Daten des Nutzers während der Sitzung

# Initialisiere den Chat-Verlauf, falls noch nicht vorhanden
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialisiere die Prozessdaten
if 'bescheid_datum' not in st.session_state:
    st.session_state.bescheid_datum = None
if 'frist_ende' not in st.session_state:
    st.session_state.frist_ende = None
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {} # Dictionary für Name und Inhalt
if 'widerspruchstext' not in st.session_state:
    st.session_state.widerspruchstext = ""


# --- FUNKTIONEN ---------------------------------------------------------------

def get_document_context():
    """Erstellt einen Text-Kontext aus den hochgeladenen Dokumenten für die KI."""
    if not st.session_state.uploaded_files:
        return "Der Nutzer hat noch keine Dokumente hochgeladen."
    
    context = "Der Nutzer hat folgende Dokumente hochgeladen:\n"
    for filename, content in st.session_state.uploaded_files.items():
        context += f"- Dateiname: {filename}\n"
        # Hier könnte man den Inhalt der Datei (z.B. per OCR) auslesen.
        # Fürs Erste geben wir nur die Dateinamen und eine Inhaltsnotiz.
        # Wenn der Inhalt Text ist, können wir die ersten Zeichen anzeigen.
        try:
            # Versuche, den Inhalt als Text zu dekodieren
            decoded_content = base64.b64decode(content).decode('utf-8', errors='ignore')
            preview = decoded_content[:200]
            context += f"  Vorschau des Inhalts: '{preview}...'\n"
        except Exception:
            context += "  Inhalt ist kein Text (z.B. ein Bild).\n"
    
    return context

# --- LAYOUT & OBERFLÄCHE ----------------------------------------------------

st.title("⚖️ Widerspruchs-Assistent Pflegegrad")
st.markdown("Ihr persönlicher Begleiter durch den Widerspruchsprozess. **Fragen Sie mich jederzeit!**")

# Erstelle ein Zwei-Spalten-Layout
col1, col2 = st.columns([1, 1])


# --- LINKE SPALTE: PROZESS-STEUERUNG ---------------------------------------
with col1:
    st.header("1. Ihre Fristen")
    st.info("Das Wichtigste zuerst: Behalten Sie Ihre Frist im Auge.")
    
    d = st.date_input("Datum auf dem Bescheid:", value=st.session_state.bescheid_datum)
    
    if d and d != st.session_state.bescheid_datum:
        st.session_state.bescheid_datum = d
        # Berechnung der Frist (verbesserte Logik)
        try:
            zugangs_datum = d + timedelta(days=3)
            frist_ende_jahr = zugangs_datum.year + 1 if zugangs_datum.month == 12 else zugangs_datum.year
            frist_ende_monat = 1 if zugangs_datum.month == 12 else zugangs_datum.month + 1
            st.session_state.frist_ende = zugangs_datum.replace(year=frist_ende_jahr, month=frist_ende_monat)
        except ValueError: # Korrigiert den Fall für Monatsenden (z.B. 31.01. -> 28./29.02.)
            st.session_state.frist_ende = zugangs_datum.replace(year=frist_ende_jahr, month=frist_ende_monat, day=1) - timedelta(days=1)
        st.rerun()

    if st.session_state.frist_ende:
        tage_verbleibend = (st.session_state.frist_ende - date.today()).days
        if tage_verbleibend >= 0:
            st.success(f"**Fristende: {st.session_state.frist_ende.strftime('%d.%m.%Y')}** (Noch {tage_verbleibend} Tage)")
        else:
            st.error(f"**Achtung:** Die Frist ist seit {-tage_verbleibend} Tagen abgelaufen!")

    st.markdown("---")

    st.header("2. Ihre Dokumente")
    st.info("Laden Sie hier Ihren Bescheid und das MD-Gutachten hoch.")
    
    # **FEATURE: Verbessertes Datei-Handling**
    uploaded_files = st.file_uploader(
        "Dokumente (PDF, Bilder)",
        type=["pdf", "jpg", "png", "jpeg"],
        accept_multiple_files=True
    )

    if uploaded_files:
        # Speichere Dateien im Session State, um sie wieder anzuzeigen
        for file in uploaded_files:
            if file.name not in st.session_state.uploaded_files:
                # Lese den Inhalt und speichere ihn Base64-kodiert
                st.session_state.uploaded_files[file.name] = base64.b64encode(file.getvalue()).decode()
        st.rerun()
        
    # Zeige bereits hochgeladene Dateien an
    if st.session_state.uploaded_files:
        st.write("Bereits hochgeladene Dokumente:")
        for filename in st.session_state.uploaded_files.keys():
            st.markdown(f"📄 `{filename}`")

    st.markdown("---")
    
    st.header("3. Ihr Widerspruch")
    st.info("Hier können Sie den Text für Ihren Widerspruch verfassen und von der KI verbessern lassen.")
    
    st.session_state.widerspruchstext = st.text_area(
        "Entwurf für Ihren Widerspruch:",
        value=st.session_state.widerspruchstext,
        height=300,
        placeholder="Beginnen Sie hier mit Ihrem Entwurf oder bitten Sie die KI um Hilfe..."
    )
    

# --- RECHTE SPALTE: DER IMMER PRÄSENTE CHATBOT ------------------------------
with col2:
    st.header("Ihr KI-Assistent")
    
    # Anzeige des bisherigen Chat-Verlaufs
    for message in st.session_state.messages:
        with st.chat_message(message.role):
            st.markdown(message.content)

    # Eingabefeld für neue Nachrichten
    if user_prompt := st.chat_input("Stellen Sie hier Ihre Frage..."):
        # Füge Nutzernachricht zum Verlauf hinzu und zeige sie an
        st.session_state.messages.append(ChatMessage(role="user", content=user_prompt))
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # KI-Antwort generieren
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                client = MistralClient(api_key=MISTRAL_API_KEY)
                
                # Erstelle den Kontext mit allen relevanten Informationen
                document_context = get_document_context()
                system_prompt_text = (
                    "Du bist ein empathischer und hochkompetenter Assistent für Pflegegrad-Widersprüche. Deine Aufgabe ist es, dem Nutzer zu helfen. "
                    "Du hast Zugriff auf den aktuellen Kontext des Nutzers:\n"
                    f"- Datum des Bescheids: {st.session_state.bescheid_datum}\n"
                    f"- Widerspruchsfrist: {st.session_state.frist_ende}\n"
                    f"- Aktueller Entwurf des Widerspruchs: '{st.session_state.widerspruchstext}'\n"
                    f"- Informationen zu hochgeladenen Dokumenten: {document_context}\n\n"
                    "Beziehe dich in deinen Antworten auf diesen Kontext. Wenn der Nutzer z.B. fragt 'Was soll ich jetzt tun?', schau dir den Prozess an und gib eine passende Antwort. "
                    "Wenn er fragt 'Was steht in meinem Gutachten?', antworte basierend auf den Dokumenteninformationen. "
                    "Gib niemals eine Rechtsberatung, sondern hilf bei der Organisation und Formulierung."
                )
                
                system_prompt = ChatMessage(role="system", content=system_prompt_text)
                messages_for_api = [system_prompt] + st.session_state.messages
                
                chat_response = client.chat(model="mistral-small-latest", messages=messages_for_api)
                full_response = chat_response.choices[0].message.content
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                full_response = "Entschuldigung, es ist ein technischer Fehler aufgetreten."
                st.error(e)

            # Füge die Antwort des Assistenten zum Verlauf hinzu
            st.session_state.messages.append(ChatMessage(role="assistant", content=full_response))
            st.rerun() # Lade die App neu, damit alles synchron bleibt