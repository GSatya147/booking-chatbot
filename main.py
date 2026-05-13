import os
import json
from typing import Optional

from dotenv import load_dotenv
import litellm
from pydantic import BaseModel, Field
import streamlit as st

load_dotenv()

EXTRACTION_PROMPT = """
You are a strict data extractor. Extract ONLY what the user has explicitly stated. Do NOT infer or hallucinate values. Return ONLY a JSON object in this exact format, nothing else:

{"name": null, "age": null}

Replace null with the actual value only if the user explicitly mentioned it.
"""

ASSISTANT_PROMPT = "You are a booking assistant."

CONTEXT: list[dict] = []

class DetailsExtractor(BaseModel):
    name: Optional[str] = Field(default=None, description="Name of the user")
    age: Optional[int] = Field(default=None, description="age of the user")

current_bookings = DetailsExtractor()

# initialise state
if "CONTEXT" not in st.session_state:
    st.session_state.CONTEXT = []

if "current_bookings" not in st.session_state:
    st.session_state.current_bookings = DetailsExtractor()

def assistant_call():
    """
    Assistant: Friendly and engages with the user, streaming output
    """
    try:
        global CONTEXT
        temp_conv = [{"role": "system", "content": ASSISTANT_PROMPT}] + CONTEXT

        response = litellm.completion(
            model=os.getenv("MODEL_FAST"),
            api_key=os.getenv("GROQ_API_KEY"),
            messages=temp_conv,
            stream=True
            )

        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as e:
       print("Assistant exception", e)


def exctrator_call():
    """
    Exctractor: ONLY exctracts the required/relevant fields, pydantic model output
    """
    try:
        global CONTEXT
        temp_exct = [{"role": "system", "content": EXTRACTION_PROMPT}] + CONTEXT

        response = litellm.completion(
            model=os.getenv("MODEL_SMART"),
            api_key=os.getenv("GROQ_API_KEY"),
            messages=temp_exct,
            # response_format=DetailsExtractor
            # model_config = ConfigDict(frozen=False)
            )
        
        try:
            json_obj = json.loads(response.choices[0].message.content)

            global current_bookings
            for field, value in json_obj.items():
                if value is not None and value != "null" and getattr(current_bookings, field) is None:
                    setattr(current_bookings, field, value)

        except Exception as e:
            print(e)

        return current_bookings

    except Exception as e:
       print("Extractor exception: ", e)

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

        st.session_state.current_bookings = exctrator_call()
        st.rerun()

    except Exception as e:
        print(e)



