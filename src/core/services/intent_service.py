import json
from llama_index.llms.groq import Groq
from llama_index.core.llms import ChatMessage
from core.models.intents import IntentIn, IntentOut
from core.services.intent_canonicalizer import IntentCanonicalizer
from core.utils.env import get_required_env


class IntentService:
    """
    Intent service orchestration for extracting intents from user messages.
    """

    DEFAULT_INTENT_NAMES = [
        "category",
        "feature_focus",
        "purpose",
        "tone",
        "decision_context",
        "entity_primary",
        "action_intent",
    ]

    def __init__(self):
        model = get_required_env("LLM_MODEL")
        api_key = get_required_env("GROQ_API_KEY")

        self.llm = Groq(model=model, api_key=api_key)
        self.canonicalizer = IntentCanonicalizer()

    async def extract_intents(self, intent: IntentIn) -> IntentOut:
        if not intent.message:
            return IntentOut(
                extracted_intents={}
            )

        system_prompt = ChatMessage(
            role="system",
            content=(
                "You are a precise intent extractor."
                + "You must extract key information from a user message according to predefined intent names."
                + "Return only a valid JSON object. Do not include explanations or markdown formatting."
                + "Use these exact intent names: " + ", ".join(self.DEFAULT_INTENT_NAMES) + "."
                + "    For each intent:"
                + "    - Always return a short string (1-3 words)."
                + "    - If multiple options apply, choose the most specific one."
                + "    - Use consistent phrasing (e.g., \"summarize\", not \"summarize_and_explain\")."
            )
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
        extracted_intents = json.loads(cleaned) if cleaned else {}
        canonicalized_intents = self.canonicalizer.canonicalize_intents(extracted_intents)
        
        return IntentOut(extracted_intents=canonicalized_intents)

    def _clean_response(self, text: str) -> str:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]
        return cleaned.strip()

