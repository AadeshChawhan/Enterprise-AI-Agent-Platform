import os

from dotenv import load_dotenv
from groq import Groq

from backend.app.providers.base import LLMProvider


load_dotenv()


class GroqProvider(LLMProvider):
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not configured"
            )

        self.client = Groq(
            api_key=api_key
        )

    def model_available(
        self,
        model: str
    ) -> bool:
        try:
            models = self.client.models.list()

            available_models = {
                item.id
                for item in models.data
            }

            return model in available_models

        except Exception as e:
            raise RuntimeError(
                f"Unable to check Groq models: {str(e)}"
            )

    def build_conversation(
        self,
        prompt: str,
        messages: list | None = None,
        system_prompt: str = "",
    ):
        conversation = []

        if system_prompt.strip():
            conversation.append(
                {
                    "role": "system",
                    "content": system_prompt.strip(),
                }
            )

        if messages:
            for message in messages:
                conversation.append(
                    {
                        "role": message["role"],
                        "content": message["content"],
                    }
                )

        conversation.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        return conversation

    def generate_response(
        self,
        prompt: str,
        model: str,
        temperature: float,
        messages: list | None = None,
        system_prompt: str = "",
    ):
        try:
            conversation = self.build_conversation(
                prompt=prompt,
                messages=messages,
                system_prompt=system_prompt,
            )

            response = self.client.chat.completions.create(
                model=model,
                messages=conversation,
                temperature=temperature,
            )

            return response.choices[0].message.content

        except Exception as e:
            raise RuntimeError(
                f"Groq request failed: {str(e)}"
            )

    def stream_response(
        self,
        prompt: str,
        model: str,
        temperature: float,
        messages: list | None = None,
        system_prompt: str = "",
    ):
        try:
            conversation = self.build_conversation(
                prompt=prompt,
                messages=messages,
                system_prompt=system_prompt,
            )

            response = self.client.chat.completions.create(
                model=model,
                messages=conversation,
                temperature=temperature,
                stream=True,
            )

            for chunk in response:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                if delta.content:
                    yield delta.content

        except Exception as e:
            raise RuntimeError(
                f"Groq streaming failed: {str(e)}"
            )

    def generate_conversation_title(
        self,
        prompt: str,
        model: str,
    ) -> str:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Generate a short conversation title "
                            "for the user's message. "
                            "Use 3 to 7 words. "
                            "Return only the title. "
                            "Do not use quotation marks. "
                            "Do not add punctuation at the end."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.2,
            )

            title = (
                response
                .choices[0]
                .message
                .content
                .strip()
            )

            title = title.strip('"').strip("'")

            if not title:
                return "New Conversation"

            return title[:255]

        except Exception as e:
            raise RuntimeError(
                f"Groq title generation failed: {str(e)}"
            )

    def list_models(self) -> list[str]:
        try:
            models = self.client.models.list()

            excluded_keywords = (
                "whisper",
                "prompt-guard",
                "orpheus",
                "safeguard",
            )

            filtered_models = []

            for model in models.data:
                model_id = model.id.lower()

                if any(
                    keyword in model_id
                    for keyword in excluded_keywords
                ):
                    continue

                filtered_models.append(model.id)

            return filtered_models

        except Exception as e:
            raise RuntimeError(
                f"Unable to list Groq models: {str(e)}"
            )
        