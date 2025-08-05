import toml
import re
import streamlit as st
from google import genai
from google.genai import types

# Initialize session state
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

st.title("👩‍🏫 AI Teacher & Text Adventure")

# Step 1: Language input
if not st.session_state.language_chosen:
    language = st.text_input("🌐 Enter your preferred language:")
    if language:
        st.session_state.language_chosen = True

        initial_prompt = "You are the Teacher of the Future You want to Under each student on a deeper Level Under stand there Weak points and assist them in learning Knowing this Give me 5 Questions About Various Fields of Education in " + Language + " language, The Questens should be one after another ie when i finish answring 1 question then only give me the next one ,The Question Should be Brief In nature, after the last and fifth question is answered respond with Feedback for the student to his parents on how i can imporve themselfs by analazing the previous 5 Questions and feedback should be In a Short Paragraph after the feedback start the Text Based Adventure Game with Many Chapter and Each Chapter Having 4 Quests Also Make them Explain There Choices And at the end of Each Chapter evaluate it and Provide Feedback for student to his parents for every positive Interaction and consiter explainetion for the choices to assigen experience points to the interaction, And based on the Experience Point Calculate The Level and Display It when the student Asks for it"
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
