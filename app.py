import streamlit as st
import google.generativeai as genai
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
    st.warning("⚠️ style.css not found. Put it in the same folder as app.py")


# Floating icons
st.markdown("""
<div class="floating-icon">🎵</div>
<div class="floating-icon2">✨</div>
""", unsafe_allow_html=True)


# =========================
# GEMINI CONFIG (DIRECT KEY)
# =========================
API_KEY = "AIzaSyCcLnWQKXNh-iqs2ppXJTPak7NWVFAbBqg"   # 🔥 Your direct key

genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-1.5-flash"

def get_model():
    return genai.GenerativeModel(MODEL_NAME)


# =========================
# AI HELPERS
# =========================
def validate_mood_input(user_text: str) -> bool:
    model = get_model()

    prompt = f"""
    The user said: "{user_text}"

    Decide if this text expresses a mood or emotion.
    Reply ONLY "YES" or ONLY "NO".
    """

    try:
        response = model.generate_content(prompt)
        text = (response.text or "").strip().upper()
        return text.startswith("YES")
    except Exception as e:
        st.error(f"Validation error: {e}")
        return False


def generate_playlist(mood_text: str):
    model = get_model()

    prompt = f"""
    User mood: "{mood_text}"

    Recommend EXACTLY 5 songs.

    Format:
    Title - Artist - YouTube Link

    Only output 5 lines. No extra text.
    """

    try:
        response = model.generate_content(prompt)
        raw = response.text or ""
        lines = [line.strip() for line in raw.split("\n") if "-" in line]

        songs = []
        for line in lines:
            parts = line.split(" - ")
            if len(parts) >= 2:
                title = parts[0].strip()
                artist = parts[1].strip()
                link = parts[2].strip() if len(parts) > 2 else ""
                songs.append((title, artist, link))

        return songs[:5]

    except Exception as e:
        st.error(f"Error generating playlist: {e}")
        return []


def display_playlist(mood_text: str):
    with st.spinner(f"Curating vibes for “{mood_text}” 🎶"):
        time.sleep(1)
        songs = generate_playlist(mood_text)

    if not songs:
        st.error("No songs generated. Try again.")
        return

    st.markdown(
        f"<h2 class='section-title'>Recommended for: {mood_text}</h2>",
        unsafe_allow_html=True
    )

    for title, artist, link in songs:
        st.markdown(f"""
        <div class='card'>
            <div class='card-left'>
                <div class='album-img-placeholder'>💿</div>
            </div>
            <div class='card-right'>
                <div class='song-title'>{title}</div>
                <div class='song-artist'>{artist}</div>
                <a href='{link}' class='listen-btn' target='_blank'>Listen</a>
            </div>
        </div>
        """, unsafe_allow_html=True)


# =========================
# UI LAYOUT
# =========================
st.markdown("<h1 class='title'>VibeChecker</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your AI Music Curator</p>", unsafe_allow_html=True)

st.write("")
st.write("")

col1, col2, col3, col4 = st.columns(4)

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
    "",
    placeholder="Tell me how you feel… (e.g. 'lonely but hopeful')"
)

preset_moods = {
    "Energetic": "high energy upbeat hype mood",
    "Melancholy": "sad, reflective, emotional mood",
    "Chill": "relaxed, peaceful, calming mood",
    "Heartbroken": "heartbreak, missing someone deeply"
}

# =========================
# EVENT HANDLING
# =========================
if btn_energy:
    display_playlist(preset_moods["Energetic"])

elif btn_sad:
    display_playlist(preset_moods["Melancholy"])

elif btn_chill:
    display_playlist(preset_moods["Chill"])

elif btn_heart:
    display_playlist(preset_moods["Heartbroken"])

elif user_mood.strip():
    if validate_mood_input(user_mood.strip()):
        display_playlist(user_mood.strip())
    else:
        st.warning(
            "Please describe your **feelings**, not questions or instructions. Example: 'sad but hopeful'"
        )
