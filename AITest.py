import streamlit as st
from google import genai
from google.genai import types

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Gemini AI Teacher & Adventure", layout="centered")
st.title("🎓 Gemini AI Teacher & Text Adventure Game")

# --- Session State Initialization ---
if "chat" not in st.session_state:
    st.session_state.chat = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "language_submitted" not in st.session_state:
    st.session_state.language_submitted = False
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# --- Get API Key ---
api_key = st.text_input("🔑 Enter your Google Gemini API Key", type="password")

if api_key:
    try:
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[grounding_tool])

        # Create chat session once
        if st.session_state.chat is None:
            st.session_state.chat = client.chats.create(
                model='gemini-2.0-flash',
                config=config
            )

        # --- Ask for Language ---
        if not st.session_state.language_submitted:
            language = st.text_input("🌐 Enter the language you prefer", key="lang_input")
            if language:
                st.session_state.language_submitted = True
                st.session_state.language = language

                # Initial prompt to Gemini
                initial_prompt = (
                    f"You are the Teacher of the Future. You want to understand each student deeply, "
                    f"identify their weak points, and assist their learning. Generate 5 brief questions in {language} "
                    f"across different fields of education. Show one question at a time (wait for an answer before giving the next). "
                    f"After the 5th answer, analyze all answers and give feedback to the student’s parents. Then, start a Text-Based Adventure "
                    f"Game with many chapters, each having 4 quests. Ask the student to explain their choices. After each chapter, evaluate their interaction, "
                    f"assign experience points based on reasoning, and calculate level. Show the level when asked."
                )

                response = st.session_state.chat.send_message(initial_prompt)
                st.session_state.messages.append(("Gemini", response.text))
                st.rerun()

        # --- Display Chat Messages ---
        for role, message in st.session_state.messages:
            st.markdown(f"**{role}:** {message}")

        # --- User Input Callback Function ---
        def handle_user_input():
            user_input = st.session_state.user_input.strip()
            if user_input:
                response = st.session_state.chat.send_message(user_input)
                st.session_state.messages.append(("You", user_input))
                st.session_state.messages.append(("Gemini", response.text))
            # Clear input safely after submission
            st.session_state.user_input = ""

        # --- Display Input Box (Only after language is submitted) ---
        if st.session_state.language_submitted:
            st.text_input(
                "✏️ Your response",
                key="user_input",
                on_change=handle_user_input,
                placeholder="Type your answer or question and press Enter"
            )

    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.info("Please enter your Google Gemini API key to begin.")
