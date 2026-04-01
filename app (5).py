import streamlit as st
from datetime import date, timedelta
import json

st.set_page_config(
    page_title="Widerspruchshilfe Pflegegrad",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Sidebar navigation */
    section[data-testid="stSidebar"] { background: #f8faf9; }
    .main-title { font-size: 1.6rem; font-weight: 600; color: #085041; margin-bottom: 0.2rem; }
    .sub-title  { font-size: 0.95rem; color: #555; margin-bottom: 1.5rem; }

    /* Status cards */
    .status-card { background: #fff; border: 1px solid #e0e0e0; border-radius: 10px;
                   padding: 1rem 1.2rem; text-align: center; }
    .status-value { font-size: 2rem; font-weight: 700; }
    .status-label { font-size: 0.8rem; color: #666; margin-top: 0.2rem; }

    /* Module cards */
    .module-card { background: #fff; border: 1px solid #dde8e4; border-radius: 12px;
                   padding: 1.2rem; margin-bottom: 0.8rem; }
    .module-card h4 { margin: 0 0 0.3rem; color: #0F6E56; }
    .module-card p  { margin: 0; font-size: 0.88rem; color: #555; }

    /* Frist badges */
    .badge-red    { background:#fde8e8; color:#a32d2d; padding:3px 10px;
                    border-radius:20px; font-size:0.8rem; font-weight:600; }
    .badge-amber  { background:#faeeda; color:#854f0b; padding:3px 10px;
                    border-radius:20px; font-size:0.8rem; font-weight:600; }
    .badge-green  { background:#e1f5ee; color:#0f6e56; padding:3px 10px;
                    border-radius:20px; font-size:0.8rem; font-weight:600; }

    /* Result box */
    .result-box { background:#e1f5ee; border:1px solid #1d9e75; border-radius:12px;
                  padding:1.5rem; text-align:center; }
    .result-pg  { font-size:3rem; font-weight:700; color:#085041; }
    .result-lbl { font-size:0.95rem; color:#0f6e56; margin-top:0.3rem; }

    /* Widerspruch output */
    .letter-box { background:#f9f9f9; border:1px solid #ddd; border-radius:10px;
                  padding:1.5rem; font-family: 'Courier New', monospace;
                  font-size:0.88rem; line-height:1.7; white-space:pre-wrap; }

    /* Hide Streamlit footer */
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ──────────────────────────────────────────────────
if "fristen" not in st.session_state:
    st.session_state.fristen = [
        {"titel": "Widerspruch einreichen", "faellig": date.today() + timedelta(days=12),
         "beschreibung": "Bescheid vom 15.03.2025 · Pflegekasse AOK"},
        {"titel": "Ärztliches Attest einreichen", "faellig": date.today() + timedelta(days=21),
         "beschreibung": "Unterlagen für Widerspruchsakte"},
        {"titel": "Antwort Pflegekasse", "faellig": date.today() + timedelta(days=45),
         "beschreibung": "Erwartete Rückmeldung nach Einreichung"},
    ]

if "termine" not in st.session_state:
    st.session_state.termine = [
        {"titel": "Nachbegutachtung MDK", "datum": date.today() + timedelta(days=14),
         "uhrzeit": "10:00", "ort": "Zuhause"},
        {"titel": "Arztgespräch Dr. Müller", "datum": date.today() + timedelta(days=7),
         "uhrzeit": "09:30", "ort": "Praxis Müller"},
    ]

# ── Sidebar navigation ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏥 Widerspruchshilfe\n**Pflegegrad**")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["🏠 Übersicht", "⏰ Fristentracker", "📅 Kalender",
         "📋 Pflegegradrechner", "✍️ Widerspruchshilfe"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("Uni-Projekt · Prototyp")
    st.caption("⚠️ Keine Rechtsberatung")

# ═══════════════════════════════════════════════════════════════════════════
# PAGE: ÜBERSICHT
# ═══════════════════════════════════════════════════════════════════════════
if page == "🏠 Übersicht":
    st.markdown('<div class="main-title">Widerspruchshilfe Pflegegrad</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Unterstützung beim Widerspruchsprozess gegen einen Pflegegradentscheid</div>', unsafe_allow_html=True)

    # Status-Karten
    col1, col2, col3, col4 = st.columns(4)
    naechste_frist = min((f["faellig"] - date.today()).days for f in st.session_state.fristen)

    with col1:
        st.markdown(f"""<div class="status-card">
            <div class="status-value" style="color:#854f0b">{len(st.session_state.fristen)}</div>
            <div class="status-label">Aktive Fristen</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="status-card">
            <div class="status-value" style="color:#854f0b">{naechste_frist} Tage</div>
            <div class="status-label">Nächste Frist</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="status-card">
            <div class="status-value" style="color:#0F6E56">PG 3</div>
            <div class="status-label">Geschätzter Pflegegrad</div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="status-card">
            <div class="status-value" style="color:#333">{len(st.session_state.termine)}</div>
            <div class="status-label">Eingetragene Termine</div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Module")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""<div class="module-card">
            <h4>⏰ Fristentracker</h4>
            <p>Überblick über alle Fristen und Deadlines im Widerspruchsverfahren. Nie wieder eine Frist verpassen.</p>
            </div>""", unsafe_allow_html=True)
        st.markdown("""<div class="module-card">
            <h4>📋 Pflegegradrechner</h4>
            <p>Selbsteinschätzung nach NBA-System (6 Module) zur Vorbereitung und Begründung des Widerspruchs.</p>
            </div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown("""<div class="module-card">
            <h4>📅 Kalender</h4>
            <p>Alle Termine, Arztbesuche und Begutachtungen auf einen Blick – mit Fristmarkierungen.</p>
            </div>""", unsafe_allow_html=True)
        st.markdown("""<div class="module-card">
            <h4>✍️ Widerspruchshilfe</h4>
            <p>Geführte Formulierung des Widerspruchsschreibens mit individuellen Textbausteinen.</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.info("ℹ️ **Hinweis:** Dieses Tool ersetzt keine rechtliche Beratung. Bei Unsicherheiten wenden Sie sich an einen Pflegeberater oder Sozialverband (VdK, SoVD).")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: FRISTENTRACKER
# ═══════════════════════════════════════════════════════════════════════════
elif page == "⏰ Fristentracker":
    st.title("⏰ Fristentracker")
    st.caption("Behalte alle Fristen im Widerspruchsverfahren im Blick.")

    # Bestehende Fristen
    for i, frist in enumerate(st.session_state.fristen):
        tage = (frist["faellig"] - date.today()).days
        if tage <= 14:
            badge = f'<span class="badge-red">🔴 {tage} Tage</span>'
        elif tage <= 28:
            badge = f'<span class="badge-amber">🟡 {tage} Tage</span>'
        else:
            badge = f'<span class="badge-green">🟢 ~{tage} Tage</span>'

        with st.container(border=True):
            col1, col2, col3 = st.columns([4, 2, 1])
            with col1:
                st.markdown(f"**{frist['titel']}**")
                st.caption(frist["beschreibung"])
            with col2:
                st.markdown(f"Fällig: **{frist['faellig'].strftime('%d.%m.%Y')}**")
                st.markdown(badge, unsafe_allow_html=True)
            with col3:
                if st.button("🗑️", key=f"del_frist_{i}", help="Frist löschen"):
                    st.session_state.fristen.pop(i)
                    st.rerun()

    st.markdown("---")

    # Neue Frist hinzufügen
    with st.expander("➕ Neue Frist hinzufügen"):
        with st.form("neue_frist"):
            titel = st.text_input("Bezeichnung der Frist")
            beschreibung = st.text_input("Beschreibung (optional)")
            faellig = st.date_input("Fälligkeitsdatum", min_value=date.today())
            submitted = st.form_submit_button("Frist speichern", type="primary")
            if submitted and titel:
                st.session_state.fristen.append({
                    "titel": titel,
                    "beschreibung": beschreibung,
                    "faellig": faellig
                })
                st.success(f"✅ Frist '{titel}' wurde gespeichert.")
                st.rerun()

    # Info-Box zu gesetzlichen Fristen
    with st.expander("ℹ️ Gesetzliche Fristen im Überblick"):
        st.markdown("""
| Frist | Zeitraum | Hinweis |
|-------|----------|---------|
| **Widerspruch einlegen** | 4 Wochen ab Bescheid | Schriftlich bei der Pflegekasse |
| **Klage (Sozialgericht)** | 1 Monat nach Widerspruchsbescheid | Falls Widerspruch abgelehnt |
| **Rückmeldung Pflegekasse** | 3 Monate | Gesetzliche Bearbeitungszeit |
| **Neue Begutachtung beantragen** | Jederzeit | Bei Verschlechterung des Zustands |
        """)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: KALENDER
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📅 Kalender":
    st.title("📅 Kalender")
    st.caption("Alle Termine und Fristen auf einen Blick.")

    # Termine anzeigen
    st.subheader("Eingetragene Termine")

    # Fristen auch im Kalender anzeigen
    alle_eintraege = []
    for f in st.session_state.fristen:
        alle_eintraege.append({
            "datum": f["faellig"],
            "titel": f"⏰ FRIST: {f['titel']}",
            "ort": "–",
            "uhrzeit": "–",
            "typ": "frist"
        })
    for t in st.session_state.termine:
        alle_eintraege.append({**t, "typ": "termin"})

    alle_eintraege.sort(key=lambda x: x["datum"])

    for i, eintrag in enumerate(alle_eintraege):
        tage = (eintrag["datum"] - date.today()).days
        if tage < 0:
            zeitinfo = f"vor {abs(tage)} Tagen"
            color = "#999"
        elif tage == 0:
            zeitinfo = "Heute!"
            color = "#E24B4A"
        elif tage == 1:
            zeitinfo = "Morgen"
            color = "#EF9F27"
        else:
            zeitinfo = f"in {tage} Tagen"
            color = "#0F6E56"

        icon = "📌" if eintrag["typ"] == "frist" else "📆"
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"{icon} **{eintrag['titel']}**")
                st.caption(f"📅 {eintrag['datum'].strftime('%d.%m.%Y')}  |  🕐 {eintrag.get('uhrzeit','–')}  |  📍 {eintrag.get('ort','–')}")
            with col2:
                st.markdown(f"<span style='color:{color}; font-weight:600'>{zeitinfo}</span>", unsafe_allow_html=True)

    st.markdown("---")

    with st.expander("➕ Neuen Termin eintragen"):
        with st.form("neuer_termin"):
            t_titel = st.text_input("Titel des Termins")
            t_datum = st.date_input("Datum", min_value=date.today())
            col1, col2 = st.columns(2)
            with col1:
                t_uhrzeit = st.text_input("Uhrzeit (z.B. 10:00)")
            with col2:
                t_ort = st.text_input("Ort / Adresse")
            t_submit = st.form_submit_button("Termin speichern", type="primary")
            if t_submit and t_titel:
                st.session_state.termine.append({
                    "titel": t_titel, "datum": t_datum,
                    "uhrzeit": t_uhrzeit, "ort": t_ort
                })
                st.success(f"✅ Termin '{t_titel}' wurde eingetragen.")
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: PFLEGEGRADRECHNER
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📋 Pflegegradrechner":
    st.title("📋 Pflegegradrechner")
    st.caption("Selbsteinschätzung nach dem NBA-System (Neue Begutachtungs-Assessment). Alle 6 Module werden gewichtet.")

    STUFEN = ["Selbstständig (0)", "Überwiegend selbstständig (1)", "Überwiegend unselbstständig (2)", "Unselbstständig (3)"]
    STUFEN_VAL = [0, 1, 2, 3]

    # Gewichtung der Module nach NBA
    GEWICHTUNG = {
        "Mobilität": 0.10,
        "Kognitive und kommunikative Fähigkeiten": 0.15,
        "Verhaltensweisen / psychische Problemlagen": 0.15,
        "Selbstversorgung": 0.40,
        "Umgang mit krankheitsbedingten Anforderungen": 0.20,
        "Gestaltung des Alltagslebens": 0.00,  # fließt nicht direkt ein, aber relevant
    }

    def get_pflegegrad(gesamtpunkte):
        if gesamtpunkte < 12.5: return 1, "Geringe Beeinträchtigung", "#639922"
        elif gesamtpunkte < 27:  return 2, "Erhebliche Beeinträchtigung", "#EF9F27"
        elif gesamtpunkte < 47.5: return 3, "Schwere Beeinträchtigung", "#D85A30"
        elif gesamtpunkte < 70:  return 4, "Schwerste Beeinträchtigung", "#E24B4A"
        else:                    return 5, "Schwerste Beeinträchtigung (Sonderfall)", "#A32D2D"

    module_punkte = {}

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "1 · Mobilität", "2 · Kognition", "3 · Verhalten",
        "4 · Selbstversorgung", "5 · Therapie", "6 · Alltag"
    ])

    with tab1:
        st.markdown("**Modul 1 – Mobilität** *(Gewichtung: 10%)*")
        m1_1 = st.select_slider("Positionswechsel im Bett", STUFEN, key="m1_1")
        m1_2 = st.select_slider("Halten einer stabilen Sitzposition", STUFEN, key="m1_2")
        m1_3 = st.select_slider("Umsetzen", STUFEN, key="m1_3")
        m1_4 = st.select_slider("Fortbewegung innerhalb des Wohnbereichs", STUFEN, key="m1_4")
        m1_5 = st.select_slider("Treppensteigen", STUFEN, key="m1_5")
        module_punkte["Mobilität"] = sum(STUFEN.index(v) for v in [m1_1, m1_2, m1_3, m1_4, m1_5])

    with tab2:
        st.markdown("**Modul 2 – Kognitive und kommunikative Fähigkeiten** *(Gewichtung: 15%)*")
        m2_1 = st.select_slider("Örtliche Orientierung", STUFEN, key="m2_1")
        m2_2 = st.select_slider("Zeitliche Orientierung", STUFEN, key="m2_2")
        m2_3 = st.select_slider("Erkennen von Personen aus dem näheren Umfeld", STUFEN, key="m2_3")
        m2_4 = st.select_slider("Erinnern an wesentliche Ereignisse", STUFEN, key="m2_4")
        m2_5 = st.select_slider("Verstehen von Sachverhalten und Informationen", STUFEN, key="m2_5")
        module_punkte["Kognitive und kommunikative Fähigkeiten"] = sum(STUFEN.index(v) for v in [m2_1, m2_2, m2_3, m2_4, m2_5])

    with tab3:
        st.markdown("**Modul 3 – Verhaltensweisen und psychische Problemlagen** *(Gewichtung: 15%)*)")
        m3_1 = st.select_slider("Motorisch geprägte Verhaltensauffälligkeiten", STUFEN, key="m3_1")
        m3_2 = st.select_slider("Nächtliche Unruhe", STUFEN, key="m3_2")
        m3_3 = st.select_slider("Selbstschädigende Verhaltensweisen", STUFEN, key="m3_3")
        m3_4 = st.select_slider("Ängste", STUFEN, key="m3_4")
        module_punkte["Verhaltensweisen / psychische Problemlagen"] = sum(STUFEN.index(v) for v in [m3_1, m3_2, m3_3, m3_4])

    with tab4:
        st.markdown("**Modul 4 – Selbstversorgung** *(Gewichtung: 40%)*")
        m4_1 = st.select_slider("Waschen des vorderen Oberkörpers", STUFEN, key="m4_1")
        m4_2 = st.select_slider("Körperpflege im Bereich des Kopfes", STUFEN, key="m4_2")
        m4_3 = st.select_slider("Waschen des Intimbereichs", STUFEN, key="m4_3")
        m4_4 = st.select_slider("An- und Auskleiden des Oberkörpers", STUFEN, key="m4_4")
        m4_5 = st.select_slider("An- und Auskleiden des Unterkörpers", STUFEN, key="m4_5")
        m4_6 = st.select_slider("Mundgerechtes Zubereiten der Nahrung", STUFEN, key="m4_6")
        m4_7 = st.select_slider("Essen", STUFEN, key="m4_7")
        m4_8 = st.select_slider("Trinken", STUFEN, key="m4_8")
        m4_9 = st.select_slider("Benutzen einer Toilette / eines Toilettenstuhls", STUFEN, key="m4_9")
        module_punkte["Selbstversorgung"] = sum(STUFEN.index(v) for v in [m4_1,m4_2,m4_3,m4_4,m4_5,m4_6,m4_7,m4_8,m4_9])

    with tab5:
        st.markdown("**Modul 5 – Umgang mit krankheits- / therapiebedingten Anforderungen** *(Gewichtung: 20%)*")
        m5_1 = st.select_slider("Medikation", STUFEN, key="m5_1")
        m5_2 = st.select_slider("Arztbesuche / Therapien", STUFEN, key="m5_2")
        m5_3 = st.select_slider("Wundversorgung", STUFEN, key="m5_3")
        m5_4 = st.select_slider("Hilfsmittelversorgung", STUFEN, key="m5_4")
        module_punkte["Umgang mit krankheitsbedingten Anforderungen"] = sum(STUFEN.index(v) for v in [m5_1,m5_2,m5_3,m5_4])

    with tab6:
        st.markdown("**Modul 6 – Gestaltung des Alltagslebens und sozialer Kontakte**")
        m6_1 = st.select_slider("Tagesablauf gestalten und anpassen", STUFEN, key="m6_1")
        m6_2 = st.select_slider("Ruhen und Schlafen", STUFEN, key="m6_2")
        m6_3 = st.select_slider("Sozialkontakte pflegen", STUFEN, key="m6_3")
        module_punkte["Gestaltung des Alltagslebens"] = sum(STUFEN.index(v) for v in [m6_1,m6_2,m6_3])

    # Berechnung (vereinfacht nach NBA-Gewichtung)
    gesamtpunkte = (
        module_punkte["Mobilität"] * 10 / 15 +
        module_punkte["Kognitive und kommunikative Fähigkeiten"] * 15 / 15 +
        module_punkte["Verhaltensweisen / psychische Problemlagen"] * 15 / 12 +
        module_punkte["Selbstversorgung"] * 40 / 27 +
        module_punkte["Umgang mit krankheitsbedingten Anforderungen"] * 20 / 12 +
        module_punkte["Gestaltung des Alltagslebens"] * 0
    )

    pg, bezeichnung, farbe = get_pflegegrad(gesamtpunkte)

    st.markdown("---")
    st.subheader("Ergebnis der Selbsteinschätzung")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""<div class="result-box">
            <div class="result-pg" style="color:{farbe}">PG {pg}</div>
            <div class="result-lbl">{bezeichnung}</div>
            <div style="margin-top:0.5rem; font-size:0.8rem; color:#555">
                Gesamtpunkte: <b>{gesamtpunkte:.1f}</b>
            </div></div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("**Punkte je Modul:**")
        for modul, punkte in module_punkte.items():
            st.progress(min(punkte / 27, 1.0), text=f"{modul}: {punkte} Pkt.")

    st.info("⚠️ Dies ist eine Orientierungshilfe – kein offizielles Gutachten. Nutze das Ergebnis zur Vorbereitung auf das MDK-Gespräch.")

    # Punkte im Session State für Widerspruchshilfe speichern
    st.session_state["letzter_pg"] = pg
    st.session_state["letzter_pg_bezeichnung"] = bezeichnung


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: WIDERSPRUCHSHILFE
# ═══════════════════════════════════════════════════════════════════════════
elif page == "✍️ Widerspruchshilfe":
    st.title("✍️ Widerspruchshilfe")
    st.caption("Erstelle Schritt für Schritt ein individuelles Widerspruchsschreiben.")

    with st.form("widerspruch_form"):
        st.subheader("Schritt 1 – Angaben zur Person")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name der pflegebedürftigen Person")
            geburtsdatum = st.text_input("Geburtsdatum (z.B. 01.01.1945)")
        with col2:
            pflegekasse = st.text_input("Pflegekasse (z.B. AOK Bayern)")
            versichertennr = st.text_input("Versicherungsnummer (optional)")

        st.subheader("Schritt 2 – Angaben zum Bescheid")
        col3, col4 = st.columns(2)
        with col3:
            bescheid_datum = st.date_input("Datum des Bescheids")
            festgestellter_pg = st.selectbox(
                "Festgestellter Pflegegrad",
                ["Pflegegrad 1", "Pflegegrad 2", "Pflegegrad 3", "Pflegegrad 4", "Abgelehnt / Pflegegrad 0"]
            )
        with col4:
            gewuenschter_pg = st.selectbox(
                "Beantragter / erwarteter Pflegegrad",
                ["Pflegegrad 2", "Pflegegrad 3", "Pflegegrad 4", "Pflegegrad 5"]
            )
            widerspruch_grund = st.selectbox(
                "Hauptgrund des Widerspruchs",
                [
                    "Pflegegrad zu niedrig eingestuft",
                    "Begutachtung war unvollständig / zu kurz",
                    "Gesundheitszustand hat sich verschlechtert",
                    "Wichtige Diagnosen wurden nicht berücksichtigt",
                    "Tatsächlicher Hilfeaufwand wurde unterschätzt",
                ]
            )

        st.subheader("Schritt 3 – Ergänzende Angaben")
        situation = st.text_area(
            "Beschreibe die Pflegesituation kurz (wird in den Brief eingebaut)",
            placeholder="z.B.: Meine Mutter kann sich nicht mehr selbstständig anziehen, benötigt tägliche Hilfe bei der Körperpflege und kann die Wohnung nicht alleine verlassen...",
            height=100
        )
        belege = st.multiselect(
            "Welche Belege werden beigefügt?",
            ["Ärztliches Attest", "Pflegetagebuch", "Krankenhausberichte", "Medikamentenliste",
             "Gutachten eines anderen Arztes", "Fotos der Wohnsituation"]
        )

        absender_name = st.text_input("Absender (Name des Widerspruchsstellers)", placeholder="z.B. Max Mustermann (Sohn)")
        absender_adresse = st.text_input("Adresse des Absenders")

        submitted = st.form_submit_button("✉️ Widerspruchsentwurf erstellen", type="primary")

    if submitted:
        belege_text = ""
        if belege:
            belege_text = "\n\nFolgende Unterlagen füge ich diesem Widerspruch bei:\n" + "\n".join(f"- {b}" for b in belege)

        situation_text = ""
        if situation:
            situation_text = f"\n\nZur Verdeutlichung des tatsächlichen Hilfebedarfs möchte ich ergänzend ausführen:\n{situation}"

        brief = f"""{absender_name}
{absender_adresse}

{pflegekasse}
[Adresse der Pflegekasse]

{date.today().strftime('%d.%m.%Y')}


Widerspruch gegen den Bescheid vom {bescheid_datum.strftime('%d.%m.%Y')}
Versicherte Person: {name}, geb. {geburtsdatum}
{f'Versicherungsnummer: {versichertennr}' if versichertennr else ''}

Sehr geehrte Damen und Herren,

hiermit lege ich fristgerecht Widerspruch gegen den oben genannten Bescheid ein, mit dem {name} in {festgestellter_pg} eingestuft wurde.

Begründung:
{widerspruch_grund}. Nach unserer Einschätzung entspricht der festgestellte Pflegegrad nicht dem tatsächlichen Hilfebedarf. Wir sind der Überzeugung, dass mindestens {gewuenschter_pg} gerechtfertigt ist.{situation_text}

Wir beantragen daher, den Bescheid aufzuheben und eine erneute Begutachtung durch den Medizinischen Dienst unter Berücksichtigung aller vorliegenden Unterlagen und des realen Alltags- und Hilfebedarfs durchzuführen.{belege_text}

Wir bitten um schriftliche Bestätigung des Eingangs dieses Widerspruchs.

Mit freundlichen Grüßen

{absender_name}
"""
        st.markdown("---")
        st.subheader("📄 Ihr Widerspruchsentwurf")
        st.markdown(f'<div class="letter-box">{brief}</div>', unsafe_allow_html=True)

        st.download_button(
            label="⬇️ Brief als Textdatei herunterladen",
            data=brief,
            file_name=f"Widerspruch_Pflegegrad_{date.today().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

        st.success("✅ Entwurf erstellt! Bitte prüfe den Text sorgfältig, ergänze fehlende Angaben und lasse ihn ggf. von einem Pflegeberater prüfen.")
        st.warning("⚠️ Denk daran: Der Brief muss **innerhalb von 4 Wochen** nach Erhalt des Bescheids eingereicht werden!")
