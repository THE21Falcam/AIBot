
import streamlit as st
from llama_index.llms.ollama import Ollama
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.llms import ChatMessage
from llama_index.core.memory import Memory
import asyncio

st.title("StreamLitAI")

if "messages" not in st.session_state:
    st.session_state.messages = []

llm = Ollama(
    model="llama3.2:latest",
    request_timeout=120.0,
    # Manually set the context window to limit memory usage
    context_window=8000,
)

memory = Memory.from_defaults(session_id="my_session", token_limit=40000)
History = [ChatMessage(role="system", content="You are the Teacher of the Future You want to Under each student on a deeper Level Under stand there Weak points and assist them in learning Knowing this Give me 5 Questions About Various Fields of Education in English language, The Questens should be one after another ie when i finish answring 1 question then only give me the next one ,The Question Should be Brief In nature, after the last and fifth question is answered respond with Feedback for the student to his parents on how i can imporve themselfs by analazing the previous 5 Questions and feedback should be In a Short Paragraph after the feedback start the Text Based Adventure Game with Many Chapter and Each Chapter Having 4 Quests Also Make them Explain There Choices And at the end of Each Chapter evaluate it and Provide Feedback for student to his parents for every positive Interaction and consiter explainetion for the choices to assigen experience points to the interaction, And based on the Experience Point Calculate The Level and Display It when the student Asks for it")]
agent = FunctionAgent(llm=llm, tools=[])

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    memory.put_messages(History)
    chat_history = memory.get()
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    async def get_response():
        return await agent.run(prompt, chat_history=chat_history)

    response = asyncio.run(get_response())
    st.session_state.messages.append({"role": "assistant", "content": response})
    History.append(ChatMessage(role="user", content = prompt))
    History.append(ChatMessage(role="assistant", content=response))
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history

