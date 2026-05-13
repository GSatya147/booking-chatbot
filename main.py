import os
from typing import Optional

from dotenv import load_dotenv
import litellm
from pydantic import BaseModel, Field

load_dotenv()

EXTRACTION_PROMPT = "Extract only the user name from 'user' messages, and return it."

ASSISTANT_PROMPT = "You are a booking assistant. Give your introduction in 200 words"

CONTEXT: list[dict] = []

class DetailsExtractor(BaseModel):
    name: Optional[str] = Field(description="Name of the user")

def assistant_call():
    """
    Assistant: Friendly and engages with the user, streaming output
    """
    try:
        global CONTEXT
        temp_conv = [{"role": "system", "content": ASSISTANT_PROMPT}] + CONTEXT

        response = litellm.completion(
            model=os.getenv("MODEL"),
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
        temp_exct = [{"role": "system", "content": EXTRACTION_PROMPT}] + CONTEXT

        response = litellm.completion(
            model=os.getenv("MODEL"),
            api_key=os.getenv("GROQ_API_KEY"),
            messages=temp_exct,
            )

        return response.choices[0].message.content

    except Exception as e:
       print("Extractor exception: ", e)

user_prompt: str = input(">> ")
CONTEXT: list[dict] = [{"role": "user", "content": user_prompt}]

assistant_response_string = ""
for i in assistant_call():
    if i:
        assistant_response_string += i
        print(i, end="")

print(exctrator_call())

CONTEXT += [{"role": "assistant", "content": assistant_response_string}]
print(CONTEXT)
