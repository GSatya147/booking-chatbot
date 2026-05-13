import os

from dotenv import load_dotenv
import litellm

load_dotenv()

SYS_PROMPT: str = "You are a booking assistant."

SYS_PROMPT_SUMMARISE: str = (
    "summarise the entire conversation and capture important information and decisions"
)


class ConversationManager:
    def __init__(self):
        self.CONTEXT: list[dict] = []

        self.CONTEXT.append(
            {"type": "original", "role": "system", "content": SYS_PROMPT}
        )

    def add_context(self, message: str, role: str) -> list[dict]:
        message_dict = {"role": role, "content": message}

        self.CONTEXT.append(message_dict)
        return self.CONTEXT

    def trim_context(self) -> list[dict]:
        sys_list: list[dict] = [x for x in self.CONTEXT if x.get("type") == "original"]

        remaining_list: list[dict] = [
            x for x in self.CONTEXT if x.get("type") != "original"
        ]
        if len(remaining_list) > 0:
            remaining_list.pop(0)

        self.CONTEXT: list[dict] = sys_list + remaining_list

        return self.CONTEXT

    def summarise(self):
        temp_messages = self.CONTEXT + [
            {"role": "system", "content": SYS_PROMPT_SUMMARISE}
        ]

        response = litellm.completion(
            model=os.getenv("MODEL_SMART"),
            api_key=os.getenv("GROQ_API_KEY"),
            messages=temp_messages,
        )
        # response = chat(temp_messages, "local")

        self.CONTEXT = [
            {"role": "system", "content": SYS_PROMPT},
            {"role": "system", "content": response},
        ]

    def context_manage(self):
        if len(self.CONTEXT) > 4:
            self.summarise()

            if len(self.CONTEXT) > 6:
                self.trim_context()

    # def client_call(self, message: list[dict], mode: str):
    #     context = [
    #         {"role": x.get("role"), "content": x.get("content")} for x in message
    #     ]
    #     print(context)
    #     response = chat(context, mode)
    #     return response
