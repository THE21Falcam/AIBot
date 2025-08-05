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
if "initialized" not in st.session_state:
    st.session_state.initialized = False

# --- Get Gemini API Key from User ---
api_key = st.text_input("🔑 Enter your Google Gemini API Key", type="password")

# --- Proceed only if API key is provided ---
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

        # --- Language Input ---
        language = st.text_input("🌐 Enter the language you prefer")

        # If language is entered and not already initialized, send the initial prompt
        if language and not st.session_state.initialized:
            st.session_state.language = language
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
            st.session_state.initialized = True
            st.experimental_rerun()  # Rerun to immediately show the response

        # --- Display Chat Messages ---
        if st.session_state.messages:
            st.markdown("---")
            st.subheader("🧠 Gemini Response")
            for role, msg in st.session_state.messages:
                st.markdown(f"**{role}:** {msg}")

        # --- Input for User Responses ---
        user_input = st.text_input("✏️ Your response", key="user_input")

        if user_input:
            response = st.session_state.chat.send_message(user_input)
            st.session_state.messages.append(("You", user_input))
            st.session_state.messages.append(("Gemini", response.text))
            st.session_state.user_input = ""  # Clear input
            st.experimental_rerun()

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

else:
    st.info("Please enter your Gemini API key to start.")
