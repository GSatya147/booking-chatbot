import os

from dotenv import load_dotenv
import litellm

load_dotenv()

ASSISTANT_PROMPT = "You are a booking assistant."


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
            stream=True,
        )

        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as e:
        print("Assistant exception", e)
