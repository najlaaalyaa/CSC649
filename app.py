import streamlit as st
import requests
import random
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="VibeChecker", page_icon="🎵", layout="wide")

# --- LOAD CSS ---
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# --- API KEY ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ Missing API Key! Add GOOGLE_API_KEY in Streamlit Secrets.")
    st.stop()

# --- GEMINI API FUNCTION ---
def generate_playlist_from_mood(mood):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"

    prompt = f"""
    You are DJ VibeCheck.

    Generate EXACTLY 5 songs based on the mood: **{mood}**

    FORMAT STRICTLY:
    Title - Artist
    (no numbering)
    """

    data = {"contents": [{"parts": [{"text": prompt}]}]}

    response = requests.post(url, json=data)

    try:
        text = response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return []

    playlist = []
    for line in text.split("\n"):
        if "-" in line:
            title, artist = line.split("-", 1)
            playlist.append((title.strip(), artist.strip()))

    return playlist[:5]

# --- PLAYLIST CARD DISPLAY ---
def display_playlist(mood):
    with st.spinner(f"Curating {mood} vibes… 🎶"):
        time.sleep(1.2)
        playlist = generate_playlist_from_mood(mood)

    st.markdown(f"<h2 class='section-title'>Recommended for {mood}</h2>", unsafe_allow_html=True)

    if not playlist:
        st.error("⚠️ API failed to return songs.")
        return

    # Song Cards
    for title, artist in playlist:
        yt_query = f"https://www.youtube.com/results?search_query={title}+{artist}".replace(" ", "+")
        st.markdown(
            f"""
            <div class='song-card'>
                <img src='https://via.placeholder.com/90' class='album-img'>
                <div class='card-right'>
                    <div class='song-title'>{title}</div>
                    <div class='song-artist'>{artist}</div>
                    <a href='{yt_query}' target='_blank' class='listen-btn'>Listen</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Now playing bar
    first = playlist[0]
    st.markdown(
        f"""
        <div class='now-playing'>
            <span class='np-label'>Now Playing:</span> {first[0]} — {first[1]}
        </div>
        """,
        unsafe_allow_html=True
    )


# -------------------------
# MAIN UI
# -------------------------

st.markdown("<h1 class='title'>VibeChecker</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your Personal Mood-Based Music Curator</p>", unsafe_allow_html=True)

st.write("")
st.write("")

# --- Mood Buttons ---
col1, col2, col3, col4 = st.columns(4)

clicked = None

with col1:
    if st.button("⚡ Energetic", use_container_width=True):
        clicked = "Energetic"

with col2:
    if st.button("🟣 Melancholy", use_container_width=True):
        clicked = "Melancholy"

with col3:
    if st.button("🧘 Chill", use_container_width=True):
        clicked = "Chill"

with col4:
    if st.button("💔 Heartbroken", use_container_width=True):
        clicked = "Heartbroken"

# --- Surprise Me ---
if st.sidebar.button("🎲 Surprise Me"):
    moods = ["Energetic", "Melancholy", "Chill", "Heartbroken", "Calm", "Romantic", "Angry"]
    clicked = random.choice(moods)

# --- User Mood Input ---
user_mood = st.text_input(" ", placeholder="Type your mood here…").strip()
if user_mood:
    clicked = user_mood

# --- Generate Results ---
if clicked:
    display_playlist(clicked)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<div class='sidebar-container'>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-title'>🎧 Vibe Menu</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-sub'>Find the perfect playlist for your mood</div>", unsafe_allow_html=True)

    # Mood buttons
    mood_list = [
        ("⚡ Energetic", "Energetic"),
        ("🟣 Melancholy", "Melancholy"),
        ("🧘 Chill", "Chill"),
        ("💔 Heartbroken", "Heartbroken"),
        ("🔥 Angry", "Angry"),
        ("🌸 Calm", "Calm"),
        ("❤️ Romantic", "Romantic")
    ]

    for label, value in mood_list:
        if st.button(label, key=value, use_container_width=True):
            clicked = value

    st.markdown(
        "<div class='sidebar-footer'>VibeChecker 2025 • Powered by Gemini AI</div>",
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

