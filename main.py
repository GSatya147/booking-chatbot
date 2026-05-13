import streamlit as st

from src.assistant import assistant_call
from src.booking_model import DetailsExtractor
from src.conversation_manager import ConversationManager
from src.exctractor import exctractor_call

current_bookings = DetailsExtractor()

# initialise state
if "conversation_manager" not in st.session_state:
    st.session_state.conversation_manager = ConversationManager()

if "current_bookings" not in st.session_state:
    st.session_state.current_bookings = DetailsExtractor()


CONTEXT = st.session_state.CONTEXT
current_bookings = st.session_state.current_bookings

# sidebar - extracted fields
with st.sidebar:
    st.json(st.session_state.current_bookings.model_dump())

# render chat history
for message in st.session_state.CONTEXT:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Type here"):
    try:

        with st.chat_message("user"):
            st.write(prompt)

        CONTEXT += [{"role": "user", "content": prompt}]

        with st.chat_message("assistant"):
            assistant_response_string = st.write_stream(assistant_call())

        CONTEXT += [{"role": "assistant", "content": assistant_response_string}]

        st.session_state.current_bookings = exctractor_call()
        st.rerun()

    except Exception as e:
        print(e)
