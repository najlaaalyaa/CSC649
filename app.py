import streamlit as st
import requests
import base64

# --- 1. SETUP PAGE CONFIG ---
st.set_page_config(page_title="VibeChecker", page_icon="🎵", layout="centered")

# --- 2. IMAGE LOADER ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- 3. CUSTOM CSS ---
st.markdown("""
    <style>
    /* General Body */
    body {
        font-family: 'Inter', sans-serif;
        background-color: #121212;
        color: #e0e0e0;
        margin: 0;
        padding: 0;
    }

    /* Title & Subtitle */
    .title {
        text-align: center;
        font-size: 60px;
        font-weight: 900;
        background: linear-gradient(90deg, #9B4DFF, #6ACBFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 80px;
    }

    .subtitle {
        text-align: center;
        font-size: 22px;
        opacity: 0.8;
        color: #B0B0B0;
        margin-top: -10px;
    }

    /* Search Bar */
    .search-bar {
        text-align: center;
        width: 60%;
        margin: 40px auto;
    }

    .search-bar input {
        width: 100%;
        padding: 12px;
        font-size: 18px;
        border-radius: 10px;
        border: 1px solid #6ACBFF;
        background-color: #1F1F1F;
        color: #e0e0e0;
        transition: border 0.3s ease;
    }

    .search-bar input:focus {
        border: 1px solid #8E66FF;
        outline: none;
    }

    /* Playlist Section */
    .section-title {
        font-size: 28px;
        font-weight: 700;
        text-align: center;
        color: #8E66FF;
        margin-top: 40px;
    }

    /* Song Card */
    .card {
        display: flex;
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 18px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        animation: fadein 0.7s ease-in-out;
    }

    .card:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.3);
    }

    .card-left {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Remove the album placeholder */
    .album-img-placeholder {
        display: none;  /* Hidden */
    }

    .card-right {
        margin-left: 15px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .song-title {
        font-size: 22px;
        font-weight: 700;
        color: #FFF;
    }

    .song-artist {
        font-size: 16px;
        opacity: 0.7;
        margin-bottom: 10px;
        color: #B0B0B0;
    }

    /* Listen Button */
    .listen-btn {
        display: inline-block;
        background: #8E66FF;
        padding: 8px 20px;
        color: white;
        text-decoration: none;
        border-radius: 12px;
        font-size: 16px;
        transition: background 0.3s, transform 0.2s, box-shadow 0.3s ease;
        margin-top: 10px;
    }

    .listen-btn:hover {
        background: #7C55E6;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3);
        transform: translateY(-3px);
    }

    /* Sidebar */
    .sidebar {
        position: fixed;
        top: 0;
        left: 0;
        height: 100%;
        width: 250px;
        background-color: #1F1F1F;
        padding-top: 30px;
        padding-left: 20px;
    }

    .sidebar .sidebar-title {
        font-size: 24px;
        color: #8E66FF;
        font-weight: 800;
    }

    .sidebar .sidebar-sub {
        color: #B0B0B0;
        opacity: 0.7;
    }

    .sidebar .sidebar-item {
        margin: 15px 0;
        font-size: 18px;
        color: #B0B0B0;
        cursor: pointer;
    }

    .sidebar .sidebar-item:hover {
        color: #8E66FF;
    }

    .sidebar .surprise-btn {
        display: inline-block;
        background: #FF6F61;
        padding: 12px 24px;
        color: white;
        text-decoration: none;
        border-radius: 12px;
        font-size: 16px;
        margin-top: 20px;
        transition: background 0.3s ease, transform 0.2s ease;
    }

    .sidebar .surprise-btn:hover {
        background: #FF5733;
        transform: translateY(-3px);
    }

    /* Floating Icons */
    .floating-icon,
    .floating-icon2 {
        position: fixed;
        font-size: 28px;
        opacity: 0.6;
        animation: float 3s infinite ease-in-out;
        z-index: 999;
        pointer-events: none;
    }

    .floating-icon { top: 20px; right: 20px; }
    .floating-icon2 { bottom: 20px; left: 20px; }

    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(10px); }
        100% { transform: translateY(0px); }
    }

    /* Animation */
    @keyframes fadein {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. MAIN INTERFACE ---
# Title and Subtitle
st.title("🎶 VibeChecker")
st.subheader("Your Elegant AI Music Curator")

# Search Bar
search_query = st.text_input("Enter a mood...", key="mood_search", placeholder="e.g. Energetic, Chill, Rage")

# Simulate dynamic playlist section based on mood input
if search_query:
    st.markdown(f'<div class="section-title">Recommended for "{search_query}"</div>', unsafe_allow_html=True)

    # Dummy songs based on the mood query. You can replace this with a recommendation algorithm
    playlist = [
        {"title": "Song A", "artist": "Artist A", "url": "https://www.youtube.com"},
        {"title": "Song B", "artist": "Artist B", "url": "https://www.youtube.com"},
        {"title": "Song C", "artist": "Artist C", "url": "https://www.youtube.com"}
    ]
    
    for song in playlist:
        st.markdown(f"""
            <div class="card">
                <div class="card-left">
                    <div class="album-img-placeholder">💿</div>
                </div>
                <div class="card-right">
                    <div class="song-title">{song['title']}</div>
                    <div class="song-artist">{song['artist']}</div>
                    <a class="listen-btn" href="{song['url']}">▶️ Listen on YouTube</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Sidebar for mood options and surprise button
with st.sidebar:
    st.markdown('<div class="sidebar-title">How to Use</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-item">Select a mood</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-item">Let me curate</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-item">Enjoy the playlist</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Past Moods</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-item">Melancholy</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-item">Chill</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-item">Energetic</div>', unsafe_allow_html=True)
    st.markdown('<div class="surprise-btn">Surprise Me</div>', unsafe_allow_html=True)

# --- 5. ADDITIONAL CODE FOR CHAT FUNCTIONALITY ---
# You can also add a function for chat history and recommendation logic here.
