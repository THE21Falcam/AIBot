import streamlit as st
from google import genai
from google.genai import types
import re

st.title("🤖 AI Teacher + Text Adventure Game")

# Step 1: Ask for Gemini API Key
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key_input = st.text_input(
    "🔐 Enter your Gemini API Key",
    type="password",
    value=st.session_state.api_key,
    placeholder="Paste your Gemini API key here..."
)

if api_key_input and api_key_input != st.session_state.api_key:
    st.session_state.api_key = api_key_input
    st.rerun()

# Step 2: Stop execution if API key is not provided
if not st.session_state.api_key:
    st.stop()

# Step 3: Setup Gemini Chat once
if "chat" not in st.session_state:
    try:
        client = genai.Client(api_key=st.session_state.api_key)
        tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[tool])
        st.session_state.chat = client.chats.create(model="gemini-2.0-flash", config=config)
        st.session_state.messages = []
        st.session_state.language_chosen = False
        st.session_state.xp = 0
        st.session_state.level = 1
    except Exception as e:
        st.error("❌ Failed to initialize Gemini API. Please check your key.")
        st.stop()

# Step 4: Ask for preferred language
if not st.session_state.language_chosen:
    language = st.text_input("🌐 Enter your preferred language:")
    if language:
        st.session_state.language_chosen = True

        intro_prompt = f"""
You are a futuristic teacher who understands students deeply.
Your job is to identify their weak points and help them grow.

1. Ask 5 questions about different fields of education in {language}.
2. Ask one question at a time. Only give the next question after the previous one is answered.
3. Keep questions short and clear.
4. After all 5 answers, analyze and give a short feedback paragraph to the student's parents.
5. Then start a text-based adventure game divided into chapters.
   - Each chapter has 4 quests.
   - Let the student explain their choices.
   - Give feedback at the end of each chapter.
   - Reward experience points (XP) for good decisions.
   - Calculate level based on XP (100 XP = 1 level).
6. When the student types "level", tell them their current level and XP.
"""
        try:
            response = st.session_state.chat.send_message(intro_prompt)
            st.session_state.messages.append(("Gemini", response.text))
            st.rerun()
        except Exception as e:
            st.error("❌ Error sending message to Gemini.")
            st.stop()

# Step 5: Display Chat History
for role, message in st.session_state.messages:
    if role == "User":
        st.markdown(f"**You:** {message}")
    else:
        st.markdown(f"**Gemini:** {message}")

# Step 6: Chat input form (auto-clear)
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("💬 Enter your message:", key="user_input")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    st.session_state.messages.append(("User", user_input))

    if user_input.strip().lower() == "level":
        level_msg = f"🌟 Your current level is {st.session_state.level}, XP: {st.session_state.xp}"
        st.session_state.messages.append(("Gemini", level_msg))
    else:
        try:
            response = st.session_state.chat.send_message(user_input)
            st.session_state.messages.append(("Gemini", response.text))

            # Try to extract XP
            match = re.search(r'(\d+)\s*xp', response.text.lower())
            if match:
                earned = int(match.group(1))
                st.session_state.xp += earned
                st.session_state.level = st.session_state.xp // 100 + 1
                xp_msg = f"🎉 You gained {earned} XP! Current level: {st.session_state.level}"
                st.session_state.messages.append(("Gemini", xp_msg))
        except Exception as e:
            st.error("❌ Error processing your message.")
            st.stop()

    st.rerun()
