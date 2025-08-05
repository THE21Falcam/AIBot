import toml
import re
import streamlit as st
from google import genai
from google.genai import types

# Initialize session state
if "chat" not in st.session_state:
    # Load API key from environment variable
    with open('secrets.toml', 'r') as f:
        config = toml.load(f)
    api_key = config["GOOGLE_API_KEY"]
    client = genai.Client(api_key=api_key)
    grounding_tool = types.Tool(google_search=types.GoogleSearch())
    config = types.GenerateContentConfig(tools=[grounding_tool])
    st.session_state.chat = client.chats.create(model="gemini-2.0-flash", config=config)
    st.session_state.messages = []
    st.session_state.language_chosen = False
    st.session_state.xp = 0
    st.session_state.level = 1

st.title("👩‍🏫 AI Teacher & Text Adventure")

# Step 1: Language input
if not st.session_state.language_chosen:
    language = st.text_input("🌐 Enter your preferred language:")
    if language:
        st.session_state.language_chosen = True

        initial_prompt = f"""
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
        response = st.session_state.chat.send_message(initial_prompt)
        st.session_state.messages.append(("Gemini", response.text))
        st.rerun()

# Step 2: Chat UI
else:
    # Display chat history
    for role, message in st.session_state.messages:
        if role == "User":
            st.markdown(f"**You:** {message}")
        else:
            st.markdown(f"**Gemini:** {message}")

    # Input box
    user_input = st.text_input("💬 Enter your message:", key="user_input")
    if st.button("Send"):
        if user_input:
            st.session_state.messages.append(("User", user_input))

            # Handle level check
            if user_input.strip().lower() == "level":
                level_msg = f"Your current level is {st.session_state.level}, XP: {st.session_state.xp}"
                st.session_state.messages.append(("Gemini", level_msg))
            else:
                response = st.session_state.chat.send_message(user_input)
                st.session_state.messages.append(("Gemini", response.text))

                # Extract XP if present
                match = re.search(r'(\d+)\s*xp', response.text.lower())
                if match:
                    earned = int(match.group(1))
                    st.session_state.xp += earned
                    st.session_state.level = st.session_state.xp // 100 + 1
                    xp_msg = f"🎉 You gained {earned} XP! Level: {st.session_state.level}"
                    st.session_state.messages.append(("Gemini", xp_msg))
        st.rerun()
