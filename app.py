import streamlit as st
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from datetime import date, timedelta
import base64

# Füge diese Funktion am Anfang deiner app.py ein
def reset_process():
    """Setzt alle relevanten Session-State-Variablen zurück."""
    keys_to_reset = ["bescheid_datum", "frist_ende", "uploaded_files", "widerspruchstext", "messages", "file_uploader"]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

# --- GRUNDKONFIGURATION -----------------------------------------------------
st.set_page_config(
    page_title="Widerspruchs-Assistent Pflegegrad",
    page_icon="⚖️",
    layout="wide"
)

# --- CSS INJECTION FÜR DAS LAYOUT (Der "Sticky-Trick") -------------------
# Dieser CSS-Code teilt die Seite in zwei Bereiche:
# - Ein Hauptbereich, der scrollen kann.
# - Ein unterer, fixierter Bereich für die Chat-Eingabe.
st.markdown("""
<style>
    /* Hauptcontainer für die Tabs */
    .main-container {
        height: 75vh; /* ca. 75% der Bildschirmhöhe */
        overflow-y: auto; /* Erlaubt scrollen innerhalb des Tab-Bereichs */
        padding-bottom: 2rem;
    }
    /* Fixierter unterer Bereich für den Chat */
    .chat-container {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 1rem 1rem 0 1rem;
        background-color: white; /* Hintergrundfarbe für den Chat-Bereich */
        border-top: 1px solid #e6e6e6;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)


# --- SICHERHEITS- & HELFER-FUNKTIONEN -----------------------------------------
# Lade API-Key sicher
try:
    MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]
except (KeyError, FileNotFoundError):
    MISTRAL_API_KEY = "UZtiS57vajTq0Gj9kJbQGJeVldLxV6Bn" # Für lokale Entwicklung

def get_session_context():
    """Sammelt alle aktuellen Nutzerdaten für die KI."""
    context = (
        "Du bist ein empathischer und hochkompetenter Assistent für Pflegegrad-Widersprüche. Deine Aufgabe ist es, dem Nutzer zu helfen. "
        "Du hast Zugriff auf den aktuellen Kontext des Nutzers:\n"
    )
    if st.session_state.get('frist_ende'):
        context += f"- Widerspruchsfrist: {st.session_state.frist_ende.strftime('%d.%m.%Y')}\n"
    if st.session_state.get('uploaded_files'):
        context += f"- Hochgeladene Dokumente: {', '.join(st.session_state.uploaded_files.keys())}\n"
    if st.session_state.get('widerspruchstext'):
        context += f"- Aktueller Entwurf des Widerspruchs: '{st.session_state.widerspruchstext[:200]}...'\n"
    
    context += "\nBeziehe dich in deinen Antworten auf diesen Kontext. Sei proaktiv und leite den Nutzer an. Gib niemals Rechtsberatung."
    return context

# --- INITIALISIERUNG DES SESSION STATE --------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}

# --- HAUPT-INTERFACE ---------------------------------------------------------
st.title("⚖️ Widerspruchs-Assistent Pflegegrad")
st.markdown('<div class="main-container">', unsafe_allow_html=True) # Start des scrollbaren Hauptbereichs

# **FEATURE: PROZESS-TABS**
tab1, tab2, tab3, tab4 = st.tabs([
    "Schritt 1: Fristberechnung", 
    "Schritt 2: Dokumente", 
    "Schritt 3: Widerspruchstext", 
    "Schritt 4: Abschluss"
])

with tab1:
    st.header("Berechnen Sie Ihre Widerspruchsfrist")
    st.markdown("Geben Sie das Datum ein, das auf Ihrem Pflegegrad-Bescheid steht. Die Frist ist der wichtigste Teil des Prozesses!")
    
    d = st.date_input("Datum des Bescheids:", key="bescheid_datum")
    if d:
        try:
            # Berechnung der Frist (vereinfacht: 1 Monat + 3 Tage Zustellfiktion)
            zugangs_datum = d + timedelta(days=3)
            frist_ende_jahr = zugangs_datum.year + 1 if zugangs_datum.month == 12 else zugangs_datum.year
            frist_ende_monat = 1 if zugangs_datum.month == 12 else zugangs_datum.month + 1
            st.session_state['frist_ende'] = zugangs_datum.replace(year=frist_ende_jahr, month=frist_ende_monat)
        except ValueError: 
             st.session_state['frist_ende'] = zugangs_datum.replace(year=frist_ende_jahr, month=frist_ende_monat, day=1) - timedelta(days=1)
        
        tage_verbleibend = (st.session_state.frist_ende - date.today()).days
        if tage_verbleibend >= 0:
            st.success(f"**Ihre Frist endet voraussichtlich am: {st.session_state.frist_ende.strftime('%d.%m.%Y')}** (Noch {tage_verbleibend} Tage)")
        else:
            st.error(f"**Achtung:** Die Frist ist seit {-tage_verbleibend} Tagen abgelaufen!")

with tab2:
    st.header("Sammeln Sie Ihre Dokumente")
    st.markdown("Laden Sie alle relevanten Unterlagen hoch, insbesondere den **Bescheid** und das **MD-Gutachten**.")
    
    uploaded_files_list = st.file_uploader(
        "Dokumente hier hochladen...",
        type=["pdf", "jpg", "png", "jpeg"],
        accept_multiple_files=True,
        key="file_uploader"
    )
    if uploaded_files_list:
        for file in uploaded_files_list:
            if file.name not in st.session_state.uploaded_files:
                st.session_state.uploaded_files[file.name] = base64.b64encode(file.getvalue()).decode()
    
    if st.session_state.uploaded_files:
        st.write("Ihre hochgeladenen Dokumente:")
        for filename in st.session_state.uploaded_files.keys():
            st.success(f"✔️ {filename}")

with tab3:
    st.header("Formulieren Sie Ihren Widerspruch")
    st.markdown("Nutzen Sie dieses Feld, um Ihren Widerspruch zu entwerfen. Sie können jederzeit im Chat unten um Hilfe bei Formulierungen bitten.")

    st.session_state['widerspruchstext'] = st.text_area(
        "Ihr Entwurf:",
        height=400,
        key="widerspruchstext",
        placeholder="Beispiel: 'Sehr geehrte Damen und Herren, hiermit lege ich Widerspruch gegen den Bescheid vom TT.MM.JJJJ ein. Die Bewertung meiner Selbstständigkeit in den Bereichen X und Y entspricht nicht den tatsächlichen Gegebenheiten...'"
    )

with tab4:
    st.header("Abschluss und nächste Schritte")
    st.balloons()
    st.success("Sie haben alle Informationen gesammelt!")
    st.markdown("Überprüfen Sie Ihren Widerspruchstext und senden Sie ihn **unterschrieben und fristgerecht per Einschreiben** an Ihre Pflegekasse.")
    st.button("Prozess neu starten", on_click=reset_process)

st.markdown('</div>', unsafe_allow_html=True) # Ende des scrollbaren Hauptbereichs

# --- FIXIERTER CHAT-BEREICH AM UNTEREN RAND ----------------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Anzeige des Chat-Verlaufs in einem Container mit begrenzter Höhe
chat_history_container = st.container(height=200) # Feste Höhe für die Chat-Historie
with chat_history_container:
    for message in st.session_state.messages:
        with st.chat_message(message.role):
            st.markdown(message.content)

# Das eigentliche Eingabefeld
if user_prompt := st.chat_input("Stellen Sie hier Ihre Frage zum Prozess oder zu Ihren Dokumenten..."):
    # Füge Nutzernachricht zum Verlauf hinzu
    st.session_state.messages.append(ChatMessage(role="user", content=user_prompt))
    
    # KI-Antwort generieren
    try:
        client = MistralClient(api_key=MISTRAL_API_KEY)
        system_prompt = ChatMessage(role="system", content=get_session_context())
        messages_for_api = [system_prompt] + st.session_state.messages
        
        chat_response = client.chat(model="mistral-small-latest", messages=messages_for_api)
        full_response = chat_response.choices[0].message.content
        st.session_state.messages.append(ChatMessage(role="assistant", content=full_response))
        
    except Exception as e:
        st.session_state.messages.append(ChatMessage(role="assistant", content=f"Entschuldigung, ein Fehler ist aufgetreten: {e}"))
    
    st.rerun() # Lade die App neu, um die neuen Nachrichten anzuzeigen

st.markdown('</div>', unsafe_allow_html=True)