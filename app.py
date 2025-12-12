import streamlit as st
import google.generativeai as genai
import os
import base64
from io import BytesIO

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="VibeChecker",
    page_icon="🎧",
    layout="wide"
)

# ---------------------------------------------------
# LOAD CUSTOM CSS
# ---------------------------------------------------
st.markdown("""
<style>

body {
    background-color: #0d0d0f;
}

/* Title */
.title {
    text-align: center;
    font-size: 48px;
    font-weight: 700;
    color: #b99bff;
    margin-top: -20px;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #bbbbbb;
    margin-top: -15px;
}

/* Mood buttons */
.stButton>button {
    width: 100% !important;
    padding: 12px;
    border-radius: 12px;
    font-weight: 600;
    background-color: #1d1d22;
    border: 1px solid #6d4cff;
    color: #e2d9ff;
}

.stButton>button:hover {
    background-color: #6d4cff;
    color: white;
}

/* Song card */
.song-card {
    background: #18181c;
    padding: 20px;
    border-radius: 20px;
    margin-bottom: 18px;
    box-shadow: 0 0 10px rgba(150, 110, 255, 0.1);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #141418;
    padding: 20px;
}

.sidebar-title {
    font-size: 26px;
    color: #c7afff;
    font-weight: 700;
    padding-bottom: 5px;
}

.sidebar-sub {
    font-size: 14px;
    color: #888;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
with st.sidebar:
    st.markdown("<div class='sidebar-title'>🎧 VibeChecker</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-sub'>AI Mood-Based Playlist Curator</div>", unsafe_allow_html=True)
    st.write("---")
    surprise = st.button("🔮 Surprise Me")
    st.write("---")
    st.markdown("**Past Moods**")
    st.markdown("- Chill\n- Energetic\n- Melancholy")


# ---------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------

def render_song(img, title, artist, url):
    """Display a styled song card with optional image."""
    with st.container():
        st.markdown("<div class='song-card'>", unsafe_allow_html=True)

        cols = st.columns([1, 5])

        with cols[0]:
            if img:
                st.image(img, width=85)
            else:
                st.image("https://via.placeholder.com/100x100/6d4cff/FFFFFF?text=♪", width=85)

        with cols[1]:
            st.markdown(f"### {title}")
            st.markdown(f"**{artist}**")
            st.link_button("🎧 Listen", url)

        st.markdown("</div>", unsafe_allow_html=True)


def generate_playlist(mood):
    """Use Gemini to generate playlist JSON."""
    prompt = f"""
    Create a playlist for the mood: {mood}.
    Return it ONLY as JSON list like:

    [
      {{
        "title": "",
        "artist": "",
        "url": ""
      }}
    ]

    No explanation.
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    import json
    return json.loads(response.text)


# ---------------------------------------------------
# MAIN UI
# ---------------------------------------------------
st.markdown("<h1 class='title'>VibeChecker</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your Personal Mood-Based Music Curator</p>", unsafe_allow_html=True)

st.write("")
st.write("")

# Mood Buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    m1 = st.button("⚡ Energetic")
with col2:
    m2 = st.button("🟣 Melancholy")
with col3:
    m3 = st.button("🧘 Chill")
with col4:
    m4 = st.button("💔 Heartbroken")

# Text input mood
manual_mood = st.text_input(" ", placeholder="Type your mood here…")


# ---------------------------------------------------
# MOOD LOGIC
# ---------------------------------------------------
selected_mood = None

if m1: selected_mood = "Energetic"
elif m2: selected_mood = "Melancholy"
elif m3: selected_mood = "Chill"
elif m4: selected_mood = "Heartbroken"
elif surprise: selected_mood = "Surprise"
elif manual_mood: selected_mood = manual_mood


# ---------------------------------------------------
# SHOW RECOMMENDATIONS
# ---------------------------------------------------
if selected_mood:

    st.write("")
    st.markdown(
        f"<h2 style='text-align:center; color:#d8c6ff;'>Recommended for {selected_mood}</h2>",
        unsafe_allow_html=True
    )
    st.write("")

    try:
        playlist = generate_playlist(selected_mood)

        for song in playlist:
            render_song(
                img=None,
                title=song.get("title", "Unknown"),
                artist=song.get("artist", "Unknown"),
                url=song.get("url", "#")
            )

    except Exception as e:
        st.error("⚠️ Error generating playlist. Check your API key or Gemini quota.")
        st.write(e)
