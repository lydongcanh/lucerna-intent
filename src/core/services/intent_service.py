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

    INTENT_SCHEMA = {
        "category": "High-level topic of the message (e.g., 'document', 'deal', 'feature', 'issue').",
        "feature_focus": "Specific product feature or function the message relates to (e.g., 'summarization', 'translation', 'upload').",
        "purpose": "User’s goal or motivation (e.g., 'understand importance', 'compare tools', 'fix issue').",
        "tone": "Emotional tone of the message (e.g., 'neutral', 'frustrated', 'curious', 'positive').",
        "decision_context": "Context in which the user is making a decision (e.g., 'room', 'project', 'review').",
        "entity_primary": "Main entity being discussed (e.g., 'document', 'user', 'feature', 'deal').",
        "action_intent": "Core action the user wants to perform (e.g., 'summarize', 'compare', 'analyze', 'upload')."
    }

    def __init__(self):
        model = get_required_env("LLM_MODEL")
        api_key = get_required_env("GROQ_API_KEY")

        self.llm = Groq(model=model, api_key=api_key)
        self.canonicalizer = IntentCanonicalizer()

    async def extract_intents(self, intent: IntentIn) -> IntentOut:
        if not intent.message:
            return IntentOut(extracted_intents={})

        intent_guidelines = "\n".join(
            [f"- **{key}**: {desc}" for key, desc in self.INTENT_SCHEMA.items()]
        )

        system_prompt = ChatMessage(
            role="system",
            content=(
                "You are a precise and deterministic intent extractor."
                " Extract exactly the defined intents from a user message using consistent phrasing."
                " Output strictly valid JSON. Do not include explanations or markdown formatting."
                "\n\nIntent definitions:\n" + intent_guidelines +
                "\n\nRules:\n"
                "- Return only a JSON object with these exact keys.\n"
                "- Each value must be a short phrase (1–3 words).\n"
                "- If uncertain, return an empty string for that field.\n"
                "- Use consistent and generic phrasing (e.g., 'summarize', not 'summarize_and_explain').\n"
            )
        )

        user_prompt = ChatMessage(
            role="user",
            content=(
                f"Message: \"{intent.message}\"\n\n"
                "Extract intents according to the schema and return valid JSON only."
            )
        )

        response = await self.llm.achat([system_prompt, user_prompt])

        content = getattr(response.message, "content", None) or getattr(response, "message", None)
        if not content:
            return IntentOut(extracted_intents={})

        cleaned = self._clean_response(content)
        try:
            extracted_intents = json.loads(cleaned)
        except Exception:
            extracted_intents = {}

        canonicalized_intents = self.canonicalizer.canonicalize_intents(extracted_intents)
        return IntentOut(extracted_intents=canonicalized_intents)

    def _clean_response(self, text: str) -> str:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]
        return cleaned.strip()
