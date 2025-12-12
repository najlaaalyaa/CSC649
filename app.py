import streamlit as st
import requests
import base64

# --- 1. SETUP PAGE CONFIG ---
st.set_page_config(page_title="VibeChecker", page_icon="🎵", layout="centered")

# --- 2. LOAD CSS FILE ---
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# --- 3. API SETUP ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ API Key missing! Check your Secrets.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. THE BRAIN (Now with Memory!) ---
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

# --- 5. MAIN INTERFACE ---
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

