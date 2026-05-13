import json
import os

from dotenv import load_dotenv
import litellm

load_dotenv()

EXTRACTION_PROMPT = """
You are a strict data extractor. Extract ONLY what the user has explicitly stated. Do NOT infer or hallucinate values. Return ONLY a JSON object in this exact format, nothing else:

{"name": null, "age": null}

Replace null with the actual value only if the user explicitly mentioned it.
"""


def exctractor_call():
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
                if (
                    value is not None
                    and value != "null"
                    and getattr(current_bookings, field) is None
                ):
                    setattr(current_bookings, field, value)

        except Exception as e:
            print(e)

        return current_bookings

    except Exception as e:
        print("Extractor exception: ", e)
