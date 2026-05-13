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
            if chunk:
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

while True:
    try:
        user_prompt: str = input(">> ")
        CONTEXT += [{"role": "user", "content": user_prompt}]

        assistant_response_string = ""
        for i in assistant_call():
            if i:
                assistant_response_string += i
                print(i, end="")

        print(f"\n{'-' * 50}")
        print(exctrator_call())

        CONTEXT += [{"role": "assistant", "content": assistant_response_string}]

    except Exception as e:
        print(e)
        break

    except KeyboardInterrupt:
        break

