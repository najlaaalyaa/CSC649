import streamlit as st
import requests
import time
from datetime import datetime
from io import StringIO
import csv

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="VibeChecker",
    page_icon="🎵",
    layout="wide"
)

# =========================
# LOAD CSS
# =========================
try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("⚠️ style.css not found. Put it in the same folder as app.py for full styling.")

# Floating icons
st.markdown("""
<div class="floating-icon">🎵</div>
<div class="floating-icon2">✨</div>
""", unsafe_allow_html=True)

# =========================
# GEMINI HTTP CONFIG
# =========================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("❌ GEMINI_API_KEY not found in secrets. Go to Settings → Secrets and add it.")
    st.stop()

# Try models from newer → older
CANDIDATE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-1.0-pro",
    "gemini-pro",
]

if "gemini_model" not in st.session_state:
    st.session_state.gemini_model = None  # will be discovered
if "history" not in st.session_state:
    st.session_state.history = []        # will store mood + songs


def _raw_gemini_call(model: str, prompt: str):
    """Low-level HTTP call for a specific model."""
    url = (
        f"https://generativelanguage.googleapis.com/v1/"
        f"models/{model}:generateContent?key={API_KEY}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        res = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        if res.status_code == 200:
            data = res.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return 200, text
        else:
            return res.status_code, res.text
    except Exception as e:
        return 0, str(e)


def call_gemini(prompt: str) -> str:
    """
    High-level call:
    - If we already know a working model, use it.
    - If that model gives 503/overloaded, try the others.
    - Show clean messages (no raw JSON).
    """
    # If we already discovered a working model, try it first
    if st.session_state.gemini_model:
        code, text = _raw_gemini_call(st.session_state.gemini_model, prompt)
        if code == 200:
            return text
        # If overloaded or internal error, forget this model and try others
        if code in (500, 503):
            st.session_state.gemini_model = None
        else:
            st.error("⚠️ Gemini returned an error. Please check your API key / quota.")
            return ""

    # Auto-detect a working model
    transient_error = False
    auth_error = False

    for model in CANDIDATE_MODELS:
        code, text = _raw_gemini_call(model, prompt)
        if code == 200:
            st.session_state.gemini_model = model
            return text
        elif code in (500, 503):  # overloaded / internal
            transient_error = True
            continue
        elif code in (401, 403):  # auth / permission
            auth_error = True
            break
        else:
            # Other 4xx/5xx, just continue trying others
            continue

    if auth_error:
        st.error("❌ Gemini API says this key has no access to these models (401/403).")
    elif transient_error:
        st.warning("✨ Gemini is a bit busy right now. Please try again in a moment.")
    else:
        st.error("⚠️ No compatible Gemini model was found for this API key.")

    return ""


# =========================
# LANGUAGE TOGGLE
# =========================
lang = st.sidebar.radio(
    "Language / Bahasa",
    ["English", "Bahasa Melayu"],
    index=0
)

is_bm = (lang == "Bahasa Melayu")


# =========================
# BACKEND: MOOD VALIDATION
# =========================
def validate_mood_input(user_text: str) -> bool:
    """
    Return True if user_text is really describing a mood/feeling.
    Works for English + Malay.
    """
    prompt = f"""
    The user said (may be English or Malay): "{user_text}"

    Your job:
    - Decide if this text describes how the user FEELS (emotion/mood/state of mind).
    - Reply ONLY with "YES" if it's clearly a mood/feeling.
    - Reply ONLY with "NO" if it is a question, command, random text, technical issue, etc.

    Examples that should be YES:
    - "i feel sad"
    - "saya sedih"
    - "penat tapi gembira"
    - "i'm bored and lonely"
    - "seronok sangat hari ni"

    Examples that should be NO:
    - "what is 5+5?"
    - "macam mana nak masak nasi?"
    - "laptop saya rosak"
    - "open the door"
    """

    text = call_gemini(prompt)
    if not text:
        return False
    return text.strip().upper().startswith("YES")


# =========================
# BACKEND: PLAYLIST GENERATION
# =========================
def generate_playlist(mood_text: str):
    """
    Ask Gemini to generate 5 songs for the given mood.
    Returns list of (title, artist, link).
    """
    lang_hint = "Malay" if is_bm else "English"

    prompt = f"""
    You are an AI music curator.

    The user described their mood ({lang_hint} may be mixed with English):
    "{mood_text}"

    Your task:
    - Understand the emotion behind this text.
    - Recommend EXACTLY 5 songs that match the mood.
    - You can suggest songs from any language, but prefer popular tracks.

    Format each line EXACTLY like:
    Title - Artist - Suggested YouTube Link

    Do NOT use numbering or bullet points.
    Output ONLY 5 lines in that format.
    """

    text = call_gemini(prompt)
    if not text:
        return []

    lines = [line.strip() for line in text.split("\n") if "-" in line]
    songs = []

    for line in lines:
        parts = line.split(" - ")
        if len(parts) >= 2:
            title = parts[0].strip()
            artist = parts[1].strip()
            link = parts[2].strip() if len(parts) > 2 else ""
            songs.append((title, artist, link))

    return songs[:5]


# =========================
# FRONTEND: RENDER + HISTORY
# =========================
def show_playlist(mood_text: str):
    with st.spinner("Curating vibes… 🎶"):
        time.sleep(1)
        songs = generate_playlist(mood_text)

    if not songs:
        st.error("No songs generated. Try again.")
        return

    heading = "Recommended for" if not is_bm else "Cadangan untuk"
    st.markdown(
        f"<h2 class='section-title'>{heading}: {mood_text}</h2>",
        unsafe_allow_html=True,
    )

    for title, artist, link in songs:
        btn_html = (
            f"<a href='{link}' target='_blank' class='listen-btn'>Listen</a>"
            if link
            else ""
        )
        st.markdown(
            f"""
            <div class='card'>
                <div class='card-left'>
                    <div class='album-img-placeholder'>💿</div>
                </div>
                <div class='card-right'>
                    <div class='song-title'>{title}</div>
                    <div class='song-artist'>{artist}</div>
                    {btn_html}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    active_model = st.session_state.gemini_model or "Auto-detecting…"
    st.markdown(
        f"""
        <div class='now-playing'>
            <span class='np-label'>Now Playing:</span> {songs[0][0]} — {songs[0][1]}
            <br><span style="font-size: 12px; opacity: 0.7;">Model: {active_model}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ===== Save to history for CSV =====
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    for idx, (title, artist, link) in enumerate(songs, start=1):
        st.session_state.history.append(
            {
                "timestamp_utc": timestamp,
                "language": "BM" if is_bm else "EN",
                "mood_text": mood_text,
                "song_rank": idx,
                "song_title": title,
                "song_artist": artist,
                "song_link": link,
                "model": active_model,
            }
        )


def build_history_csv() -> str:
    """Convert history list → CSV string."""
    if not st.session_state.history:
        return ""
    output = StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "timestamp_utc",
            "language",
            "mood_text",
            "song_rank",
            "song_title",
            "song_artist",
            "song_link",
            "model",
        ],
    )
    writer.writeheader()
    for row in st.session_state.history:
        writer.writerow(row)
    return output.getvalue()


# =========================
# SIDEBAR UI
# =========================
with st.sidebar:
    st.markdown("<div class='sidebar-title'>🎧 VibeChecker</div>", unsafe_allow_html=True)
    st.markdown("<p class='sidebar-sub'>Your personal AI music curator.</p>", unsafe_allow_html=True)
    st.write("---")
    st.markdown("### How it works" if not is_bm else "### Cara guna")
    st.markdown(
        "1. Tell me your mood\n2. I understand your vibe\n3. I suggest songs 🎵"
        if not is_bm
        else "1. Beritahu mood anda\n2. Saya faham perasaan anda\n3. Saya cadangkan lagu 🎵"
    )
    st.write("---")
    st.markdown("### Quick moods" if not is_bm else "### Mood pantas")
    st.markdown("- Energetic\n- Chill\n- Melancholy\n- Heartbroken")
    st.write("---")
    active = st.session_state.gemini_model or "Auto-detecting…"
    st.caption(f"Using Gemini model: {active}")

    # Download history CSV
    if st.session_state.history:
        csv_data = build_history_csv()
        st.download_button(
            label="⬇️ Download mood & songs history (CSV)",
            data=csv_data,
            file_name="vibechecker_history.csv",
            mime="text/csv",
        )

# =========================
# MAIN GUI
# =========================
title_text = "VibeChecker"
subtitle_text = (
    "Your Personal AI Music Curator"
    if not is_bm
    else "Kurator Muzik AI Peribadi Anda"
)

st.markdown(f"<h1 class='title'>{title_text}</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='subtitle'>{subtitle_text}</p>", unsafe_allow_html=True)

st.write("")
st.write("")

col1, col2, col3, col4 = st.columns(4)

preset_moods = {
    "Energetic": "high energy, upbeat, want to dance or work out",
    "Melancholy": "sad, reflective, emotional",
    "Chill": "relaxed, calm, peaceful background vibes",
    "Heartbroken": "heartbreak, missing someone deeply",
}

with col1:
    btn_energy = st.button("⚡ Energetic", use_container_width=True)
with col2:
    btn_sad = st.button("🟣 Melancholy", use_container_width=True)
with col3:
    btn_chill = st.button("🧘 Chill", use_container_width=True)
with col4:
    btn_heart = st.button("💔 Heartbroken", use_container_width=True)

st.write("")
st.write("")

placeholder = (
    "e.g. 'lonely but hopeful', 'stressed and tired', 'super happy today'"
    if not is_bm
    else "cth. 'sedih tapi lega', 'letih dan stres', 'seronok sangat hari ni'"
)

label = "Tell me how you feel..." if not is_bm else "Beritahu saya bagaimana perasaan anda..."

user_mood = st.text_input(label, placeholder=placeholder)

# =========================
# EVENT HANDLING
# =========================
if btn_energy:
    show_playlist(preset_moods["Energetic"])
elif btn_sad:
    show_playlist(preset_moods["Melancholy"])
elif btn_chill:
    show_playlist(preset_moods["Chill"])
elif btn_heart:
    show_playlist(preset_moods["Heartbroken"])
elif user_mood.strip():
    if validate_mood_input(user_mood):
        show_playlist(user_mood)
    else:
        msg = (
            "✨ I can recommend music, but first tell me how you feel emotionally "
            "(e.g. 'sad but hopeful', 'stressed and tired', 'super excited')."
            if not is_bm
            else "✨ Saya boleh cadangkan lagu, tapi beritahu dulu perasaan anda "
                 "(cth. 'sedih tapi lega', 'stres dan penat', 'teruja sangat')."
        )
        st.warning(msg)
