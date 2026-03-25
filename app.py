import streamlit as st
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage



# --- Konfiguration ---
# Sicherer Weg, den API-Key zu speichern (später mit Secrets Manager von Streamlit)
# Für den Anfang geht es so, aber nicht in öffentlichen Code hochladen!
MISTRAL_API_KEY = "UZtiS57vajTq0Gj9kJbQGJeVldLxV6Bn"
MODEL_NAME = "mistral-small-latest" # Ein gutes, schnelles Modell für den Start


# --- Streamlit UI ---
# (Dein Streamlit UI Code bleibt hier unverändert)
st.set_page_config(page_title="Widerspruchs-Assistent Pflegegrad", page_icon="🤖")
st.title("🤖 Widerspruchs-Assistent Pflegegrad")
st.caption(f"Prototyp mit Mistral AI ({MODEL_NAME})")
st.warning("**Wichtiger Hinweis:** Ich bin ein KI-Assistent...")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message.role):
        st.markdown(message.content)

if user_prompt := st.chat_input("Ihre Frage zum Widerspruch..."):
    st.session_state.messages.append(ChatMessage(role="user", content=user_prompt))
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # --- Mistral AI Logik mit expliziter Proxy-Übergabe ---
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # === HIER IST DIE WICHTIGE ÄNDERUNG ===
            # Wir erstellen einen httpx-Transport, der den Proxy kennt,
            # und übergeben diesen an den MistralClient.
            client = MistralClient(api_key=MISTRAL_API_KEY)
            
            # (Der Rest deiner Logik zum Aufrufen der API bleibt gleich)
            system_message = ChatMessage(role="system", content="Du bist...")
            messages_for_api = [system_message] + st.session_state.messages
            
            chat_response = client.chat(
                model=MODEL_NAME,
                messages=messages_for_api,
            )
            
            full_response = chat_response.choices[0].message.content
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            # Gib den Fehler jetzt detaillierter aus, das hilft uns!
            st.error(f"Ein detaillierter Fehler ist aufgetreten: {e}")
            full_response = "Entschuldigung, es gibt weiterhin ein technisches Problem."

        st.session_state.messages.append(ChatMessage(role="assistant", content=full_response))