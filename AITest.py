import streamlit as st
from google import genai
from google.genai import types

# --- Streamlit App Setup ---
st.set_page_config(page_title="Gemini AI Teacher & Adventure", layout="centered")
st.title("🎓 Gemini AI Teacher & Text Adventure Game")

# --- Session State Setup ---
if "chat" not in st.session_state:
    st.session_state.chat = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "language_submitted" not in st.session_state:
    st.session_state.language_submitted = False

# --- Get Gemini API Key ---
api_key = st.text_input("🔑 Enter your Google Gemini API Key", type="password")

# --- Proceed when key is present ---
if api_key:
    try:
        # Initialize Gemini Client
        client = genai.Client(api_key=api_key)
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[grounding_tool])

        # Initialize chat only once
        if st.session_state.chat is None:
            st.session_state.chat = client.chats.create(
                model='gemini-2.0-flash',
                config=config
            )

        # Input for language
        if not st.session_state.language_submitted:
            language = st.text_input("🌐 Enter the language you prefer", key="lang_input")

            if language:
                # Mark language as submitted
                st.session_state.language_submitted = True
                st.session_state.language = language

                # Send initial prompt
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

        # Display message history
        for role, msg in st.session_state.messages:
            st.markdown(f"**{role}:** {msg}")

        # Input box for user responses (after language is given)
        if st.session_state.language_submitted:
            user_input = st.text_input("✏️ Your response", key="user_input")

            if user_input:
                response = st.session_state.chat.send_message(user_input)
                st.session_state.messages.append(("You", user_input))
                st.session_state.messages.append(("Gemini", response.text))
                st.session_state.user_input = ""  # Clear input
                st.rerun()

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
else:
    st.info("Please enter your Gemini API key to begin.")
