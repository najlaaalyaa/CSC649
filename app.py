import streamlit as st
import google.generativeai as genai
import time
import random

# ============= PAGE CONFIG =============
st.set_page_config(page_title="VibeChecker", page_icon="🎵", layout="wide")

# ============= LOAD CSS =============
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

# ============= GEMINI CONFIG (BACKEND) =============
# In Streamlit Cloud → Settings → Secrets, you must add:
# GEMINI_API_KEY = "your-real-key"
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("❌ GEMINI_API_KEY not found in secrets. Go to app Settings → Secrets and add it.")
    st.stop()

MODEL_NAME = "gemini-1.5-flash"  # requires google-generativeai>=0.7.0

genai.configure(api_key=API_KEY)

def get_model():
    return genai.GenerativeModel(MODEL_NAME)

# ============= AI HELPERS (BACKEND LOGIC) =============
def validate_mood_input(user_text: str) -> bool:
    """Return True if text is a mood/feeling, False if random/question."""
    model = get_model()
    prompt = f"""
    The user said: "{user_text}"

    Your job:
    - Decide if this text describes how the user FEELS (emotion/mood/state of mind).
    - Reply ONLY with "YES" if it's clearly a mood/feeling.
    - Reply ONLY with "NO" if it is a question, command, random text, technical issue, etc.
    """

    try:
        resp = model.generate_content(prompt)
        text = (resp.text or "").strip().upper()
        return text.startswith("YES")
    except Exception as e:
        st.error(f"Validation error: {e}")
        return False


def generate_playlist(mood_text: str):
    """
    Ask Gemini to generate 5 songs: (title, artist, youtube_link)
    """
    model = get_model()
    prompt = f"""
    You are an AI music curator.

    User mood description:
    "{mood_text}"

    Recommend EXACTLY 5 songs that fit this mood.
    Use mix of modern & classic if suitable.

    Format each line EXACTLY like:
    Title - Artist - Suggested YouTube Link

    Do NOT add numbering or extra commentary. Only 5 lines.
    """

    try:
        resp = model.generate_content(prompt)
        raw = resp.text or ""
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


def show_playlist(mood_text: str):
    """Frontend rendering of the playlist cards."""
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

# ============= SIDEBAR (FRONTEND) =============
with st.sidebar:
    st.markdown("<div class='sidebar-title'>🎧 VibeChecker</div>", unsafe_allow_html=True)
    st.markdown("<p class='sidebar-sub'>Your personal AI music curator.</p>", unsafe_allow_html=True)
    st.write("---")
    st.markdown("### How it works")
    st.markdown("1. Tell me your mood\n2. I understand your vibe\n3. I suggest songs 🎵")
    st.write("---")
    st.markdown("### Quick moods")
    st.markdown("- Energetic\n- Chill\n- Melancholy\n- Heartbroken")

# ============= MAIN GUI =============
st.markdown("<h1 class='title'>VibeChecker</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your Personal AI Music Curator</p>", unsafe_allow_html=True)

st.write("")
st.write("")

col1, col2, col3, col4 = st.columns(4)
preset_moods = {
    "Energetic": "high energy, upbeat, want to dance or work out",
    "Melancholy": "sad, reflective, emotional, maybe rainy vibes",
    "Chill": "relaxed, calm, peaceful background vibes",
    "Heartbroken": "heartbreak, missing someone, breakup mood",
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

# ============= EVENT HANDLING (BACKEND + FRONTEND) =============

if btn_energy:
    show_playlist(preset_moods["Energetic"])
elif btn_sad:
    show_playlist(preset_moods["Melancholy"])
elif btn_chill:
    show_playlist(preset_moods["Chill"])
elif btn_heart:
    show_playlist(preset_moods["Heartbroken"])
elif user_mood.strip():
    # only generate if it’s actually a mood
    if validate_mood_input(user_mood):
        show_playlist(user_mood)
    else:
        st.warning(
            "✨ I can recommend music, but first tell me how you feel emotionally "
            "(e.g. 'sad but hopeful', 'stressed and tired', 'super excited')."
        )
