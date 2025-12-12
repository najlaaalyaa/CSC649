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
try:
    img_base64 = get_base64_of_bin_file("background.jpeg")
    background_style = f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("data:image/jpeg;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
    """
except:
    background_style = "<style>.stApp { background-color: #0E1117; }</style>"

st.markdown(background_style, unsafe_allow_html=True)

st.markdown("""
    <style>
    body {
    font-family: 'Inter', sans-serif;
    background-color: #121212;
    color: #e0e0e0;
    margin: 0;
    padding: 0;
}

/* Title & subtitle */
.title {
    text-align: center;
    font-size: 60px;
    font-weight: 900;
    background: linear-gradient(90deg, #b86cff, #6acbff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-top: 70px;
}

.subtitle {
    text-align: center;
    font-size: 22px;
    opacity: 0.8;
    margin-top: -10px;
    color: #b0b0b0;
    letter-spacing: 1px;
}

/* Section title */
.section-title {
    font-size: 28px;
    margin-top: 40px;
    font-weight: 700;
    text-align: center;
    color: #8e66ff;
}

/* Song card */
.card {
    display: flex;
    background: rgba(255, 255, 255, 0.1);
    padding: 18px;
    border-radius: 20px;
    margin-bottom: 18px;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    animation: fadein 0.7s ease-in-out;
    transition: transform 0.3s ease;
}

.card:hover {
    transform: scale(1.05) translateY(-5px);
}

.card-left {
    display: flex;
    align-items: center;
    justify-content: center;
}

.album-img-placeholder {
    width: 100px;
    height: 100px;
    border-radius: 16px;
    background: #3a3a3a;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 36px;
    color: #fff;
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
    color: #fff;
}

.song-artist {
    font-size: 16px;
    opacity: 0.7;
    margin-bottom: 8px;
    color: #b0b0b0;
}

.listen-btn {
    display: inline-block;
    background: #8e66ff;
    padding: 8px 18px;
    color: white;
    text-decoration: none;
    border-radius: 12px;
    font-size: 16px;
    transition: transform 0.1s ease, box-shadow 0.1s ease, background 0.2s ease;
    margin-top: 10px;
}

.listen-btn:hover {
    background: #7c55e6;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
    transform: translateY(-2px);
}

/* Now playing bar */
.now-playing {
    margin-top: 30px;
    font-size: 18px;
    background: #1f1f1f;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    color: #fff;
}

.np-label {
    font-weight: 700;
    color: #b17cff;
}

/* Animation */
@keyframes fadein {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Sidebar */
.sidebar-title {
    font-size: 28px;
    font-weight: 800;
    color: #8e66ff;
}

.sidebar-sub {
    opacity: 0.7;
    color: #b0b0b0;
}

/* Floating icons */
.floating-icon,
.floating-icon2 {
    position: fixed;
    font-size: 30px;
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

/* Chatbox */
.chatbox {
    background: rgba(255, 255, 255, 0.1);
    padding: 20px;
    border-radius: 20px;
    margin-top: 30px;
    backdrop-filter: blur(12px);
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4);
}

.chatbox input[type="text"] {
    background-color: rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    border: none;
    padding: 12px;
    width: 80%;
    font-size: 16px;
    color: white;
}

.chatbox button {
    background-color: #8e66ff;
    padding: 12px 24px;
    font-size: 16px;
    border-radius: 12px;
    border: none;
    color: white;
    transition: background 0.3s;
}

.chatbox button:hover {
    background-color: #7c55e6;
}
    </style>
""", unsafe_allow_html=True)

# --- 4. API SETUP ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ API Key missing! Check your Secrets.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. THE BRAIN (Now with Memory!) ---
def get_vibe_check():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    # 1. BUILD HISTORY
    conversation_history = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        conversation_history.append({"role": role, "parts": [{"text": msg["content"]}]})

    # 2. THE SYSTEM INSTRUCTION
    system_prompt = (
        "You are DJ VibeCheck. "
        "Goal: Recommend 5 songs based on the user's mood.\n"
        "RULES:\n"
        "1. IF the user says 'I'm not sure': Ask exactly 3 short, simple questions to help identify their mood. Do not recommend songs yet.\n"
        "2. IF the user answers your questions OR states a mood: \n"
        "   - First, briefly state what mood you think they are feeling (e.g., 'It sounds like you're feeling reflective...').\n"
        "   - Then, provide the playlist.\n"
        "3. IF the input is gibberish/random: Say 'ERROR_INVALID'.\n\n"
        "PLAYLIST FORMAT (Strict):\n"
        "1. **Song Title** - Artist\n"
        "   [▶️ Listen](https://www.youtube.com/results?search_query=Song+Title+Artist)\n"
        "   *One short sentence description.*"
    )

    # 3. SEND REQUEST
    data = {
        "contents": conversation_history,
        "systemInstruction": {"parts": [{"text": system_prompt}]}
    }
    
    try:
        res = requests.post(url, headers=headers, json=data)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        return "⚠️ Connection Error."
    except:
        return "⚠️ Network Error."

# --- 6. SIDEBAR ---
with st.sidebar:
    st.title("🎧 Control Panel")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- 7. MAIN INTERFACE ---
st.markdown('<p class="title-text">🎵 VibeChecker</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Your Personal AI Music Curator</p>', unsafe_allow_html=True)

# HERO SECTION (Quick Buttons)
if len(st.session_state.messages) == 0:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #fff; text-shadow: 1px 1px 2px black;'>How are you feeling right now?</h4>", unsafe_allow_html=True)
    
    # ROW 1
    col1, col2, col3, col4 = st.columns(4)
    clicked_mood = None
    
    with col1:
        if st.button("⚡ Energetic"): clicked_mood = "I'm feeling super energetic!"
    with col2:
        if st.button("🌧️ Melancholy"): clicked_mood = "I'm feeling sad and melancholy."
    with col3:
        if st.button("🧘‍♂️ Chill"): clicked_mood = "I want to relax and chill."
    with col4:
        if st.button("💔 Heartbroken"): clicked_mood = "I'm heartbroken."

    # ROW 2 - The New Feature
    st.write("") # Spacer
    c1, c2, c3 = st.columns([1, 2, 1]) # Centered column
    with c2:
        # This triggers the Question Flow
        if st.button("🤔 Not sure how I feel?"): 
            clicked_mood = "I'm not sure how I feel. Ask me 3 simple questions to figure it out."

    if clicked_mood:
        st.session_state.messages.append({"role": "user", "content": clicked_mood})
        st.rerun()

# CHAT HISTORY
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🎧"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# INPUT & LOGIC
if prompt := st.chat_input("Type your mood or answer here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# GENERATE RESPONSE
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar="🎧"):
        with st.spinner("Thinking..."):
            response = get_vibe_check()
            
            if "ERROR_INVALID" in response:
                response = "🚫 I didn't catch that. Tell me a real emotion!"
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

