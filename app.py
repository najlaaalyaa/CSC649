import streamlit as st
import requests
import time
import random

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
# GEMINI CONFIG (HTTP API)
# =========================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("❌ GEMINI_API_KEY not found in secrets. Go to Settings → Secrets and add it.")
    st.stop()

GEMINI_MODEL = "gemini-1.5-flash"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1/"
    f"models/{GEMINI_MODEL}:generateContent?key={API_KEY}"
)

def call_gemini(prompt: str) -> str:
    """
    Call Gemini via HTTP API and return the response text.
    """
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    try:
        res = requests.post(
            GEMINI_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        if res.status_code != 200:
            # Show real error so we know what is happening
            st.error(f"API error {res.status_code}: {res.text}")
            return ""
        data = res.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        st.error(f"Network error: {e}")
        return ""

# =========================
# BACKEND: MOOD VALIDATION
# =========================
def validate_mood_input(user_text: str) -> bool:
    """
    Return True if user_text is really describing a mood/feeling.
    """
    prompt = f"""
    The user said: "{user_text}"

    Your job:
    - Decide if this text describes how the user FEELS (emotion/mood/state of mind).
    - Reply ONLY with "YES" if it's clearly a mood/feeling.
    - Reply ONLY with "NO" if it is a question, command, random text, technical issue, etc.
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
    prompt = f"""
    You are an AI music curator.

    User mood description:
    "{mood_text}"

    Recommend EXACTLY 5 songs that fit this mood.
    Use a mix of modern and classic tracks if suitable.

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
# FRONTEND: RENDER PLAYLIST
# =========================
def show_playlist(mood_text: str):
    with st.spinner(f"Curating vibes for “{mood_text}” 🎶"):
        time.sleep(1)
        songs = generate_playlist(mood_text)

    if not songs:
        st.error("No songs generated. Try again.")
        return

    st.markdown(
        f"<h2 class='section-title'>Recommended for: {mood_text}</h2>",
        unsafe_allow_html=True,
    )

    for title, artist, link in songs:
        btn_html = f"<a href='{link}' target='_blank' class='listen-btn'>Listen</a>" if link else ""
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

    st.markdown(
        f"""
        <div class='now-playing'>
            <span class='np-label'>Now Playing:</span> {songs[0][0]} — {songs[0][1]}
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================
# SIDEBAR UI
# =========================
with st.sidebar:
    st.markdown("<div class='sidebar-title'>🎧 VibeChecker</div>", unsafe_allow_html=True)
    st.markdown("<p class='sidebar-sub'>Your personal AI music curator.</p>", unsafe_allow_html=True)
    st.write("---")
    st.markdown("### How it works")
    st.markdown("1. Tell me your mood\n2. I understand your vibe\n3. I suggest songs 🎵")
    st.write("---")
    st.markdown("### Quick moods")
    st.markdown("- Energetic\n- Chill\n- Melancholy\n- Heartbroken")

# =========================
# MAIN GUI
# =========================
st.markdown("<h1 class='title'>VibeChecker</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your Personal AI Music Curator</p>", unsafe_allow_html=True)

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

user_mood = st.text_input(
    "Tell me how you feel...",
    placeholder="e.g. 'lonely but hopeful', 'stressed and tired', 'super happy today'",
)

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
        st.warning(
            "✨ I can recommend music, but first tell me how you feel emotionally "
            "(e.g. 'sad but hopeful', 'stressed and tired', 'super excited')."
        )
