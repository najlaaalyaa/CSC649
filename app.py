import streamlit as st
import google.generativeai as genai
import time
import random

# =========================
# STREAMLIT PAGE CONFIG
# =========================
st.set_page_config(page_title="VibeChecker", page_icon="🎵", layout="wide")

# =========================
# LOAD CSS
# =========================
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Floating icons
st.markdown("""
<div class="floating-icon">🎵</div>
<div class="floating-icon2">✨</div>
""", unsafe_allow_html=True)

# =========================
# CONFIGURE GEMINI
# =========================
# Important: Do NOT hardcode API key in GitHub
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-1.5-flash"

def get_model():
    return genai.GenerativeModel(MODEL_NAME)

# =========================
# AI HELPERS
# =========================
def validate_mood_input(text):
    model = get_model()

    prompt = f"""
    The user said: "{text}"

    Decide if this text expresses a mood or emotion.
    Reply with ONLY "YES" or ONLY "NO".
    """

    try:
        reply = model.generate_content(prompt).text.strip().upper()
        return reply.startswith("YES")
    except:
        return False


def generate_playlist(mood_text):
    model = get_model()

    prompt = f"""
    User mood: "{mood_text}"

    Recommend EXACTLY 5 songs.
    Format:
    Title - Artist - YouTube Link
    """

    try:
        reply = model.generate_content(prompt).text
        lines = [line for line in reply.split("\n") if "-" in line]
        results = []

        for line in lines:
            parts = line.split(" - ")
            if len(parts) >= 2:
                title = parts[0]
                artist = parts[1]
                link = parts[2] if len(parts) >= 3 else ""
                results.append((title, artist, link))

        return results[:5]

    except Exception as e:
        st.error(f"Error: {e}")
        return []


# =========================
# UI LAYOUT
# =========================
st.markdown("<h1 class='title'>VibeChecker</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your AI Music Curator</p>", unsafe_allow_html=True)

st.write("")

col1, col2, col3, col4 = st.columns(4)

preset_moods = {
    "Energetic": "high energy upbeat hype mood",
    "Melancholy": "sad, reflective, emotional mood",
    "Chill": "calm, peaceful, relaxing vibe",
    "Heartbroken": "broken heart, missing someone deeply"
}

with col1:
    btn_energy = st.button("⚡ Energetic")
with col2:
    btn_sad = st.button("🟣 Melancholy")
with col3:
    btn_chill = st.button("🧘 Chill")
with col4:
    btn_heart = st.button("💔 Heartbroken")

st.write("")

user_mood = st.text_input("", placeholder="Tell me how you feel… (e.g. 'lonely but hopeful')")

# =========================
# DISPLAY PLAYLIST
# =========================
def display_playlist(mood_text):
    with st.spinner(f"Generating playlist for: {mood_text} 🎶"):
        time.sleep(1)
        songs = generate_playlist(mood_text)

    if not songs:
        st.error("No songs generated. Try again.")
        return

    st.markdown(f"<h2 class='section-title'>Recommended for: {mood_text}</h2>", unsafe_allow_html=True)

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
# EVENT FLOW
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
    if validate_mood_input(user_mood):
        display_playlist(user_mood)
    else:
        st.warning("Please describe your **feelings**, not questions or commands.")

