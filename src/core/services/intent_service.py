import json
from llama_index.llms.groq import Groq
from llama_index.core.llms import ChatMessage
from core.models.intents import IntentIn, IntentOut
from core.utils.env import get_required_env


class IntentService:
    DEFAULT_INTENT_NAMES = [
        "entity_primary",
        "category",
        "feature_focus",
        "purpose",
        "decision_context",
        "tone",
        "action_intent",
    ]

    def __init__(self):
        model = get_required_env("LLM_MODEL")
        api_key = get_required_env("GROQ_API_KEY")

        self.llm = Groq(model=model, api_key=api_key)

    async def extract_intents(self, intent: IntentIn) -> IntentOut:
        if not intent.message:
            return IntentOut(
                extracted_intents={}
            )

        system_prompt = ChatMessage(
            role="system",
            content=(
                "You are a precise intent extractor. "
                "You must extract key information from a user message according to predefined intent names. "
                "Return only a valid JSON object. Do not include explanations or markdown formatting."
            ),
        )

        user_prompt = ChatMessage(
            role="user",
            content=(
                f"""You must extract the following intents from the message below.
                Intents: {self.DEFAULT_INTENT_NAMES}

                Message: "{intent.message}"

                Guidelines:
                - Only extract values relevant to each intent.
                - If an intent is not found, use an empty string.
                - Keep values short and meaningful.
                - Output must be a valid JSON object with keys exactly matching the intent names.

                Now, extract the intents for the message above and return only JSON.
                """
            )
        )

        response = await self.llm.achat([system_prompt, user_prompt])

        content = getattr(response.message, "content", None) or getattr(response, "message", None)
        if not content:
            return IntentOut(extracted_intents={})

        cleaned = self._clean_response(content)
        extracted_intents = await self._parse_or_retry(cleaned, intent, system_prompt)

        return IntentOut(extracted_intents=extracted_intents)

    def _clean_response(self, text: str) -> str:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]
        return cleaned.strip()

    async def _parse_or_retry(self, content: str, intent: IntentIn, system_prompt: ChatMessage) -> dict:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            clarification = ChatMessage(
                role="user",
                content=(
                    f"The previous response was not valid JSON. "
                    f"Please correct it and return only valid JSON with keys {intent.intent_names}."
                ),
            )
            try:
                retry_response = await self.llm.achat([system_prompt, clarification])
                retry_content = self._clean_response(
                    getattr(retry_response.message, "content", None)
                    or getattr(retry_response, "message", None)
                    or ""
                )
                return json.loads(retry_content)
            except Exception:
                return { "raw_response": content }
