import os
import json

from llama_index.llms.groq import Groq
from llama_index.core.llms import ChatMessage
from core.models.intents import IntentIn, IntentOut

class IntentService:
    def __init__(self):
        model = os.getenv("LLM_MODEL")
        api_key = os.getenv("GROQ_API_KEY")
        if model is None or api_key is None:
            raise ValueError("LLM_MODEL and GROQ_API_KEY environment variables must be set")
        
        self.llm = Groq(model=model, api_key=api_key)


    async def extract_intents(self, intent: IntentIn) -> IntentOut:
        system_prompt = ChatMessage(role="system", content="You are a intent extractor.")
        user_prompt = ChatMessage(
            role="user", 
            content=f"""
            Extract the {intent.intent_names} from the following message: {intent.message}. 
            Return result as a json dict with intent names as keys and their values as the extracted text.
            """)
        
        response = await self.llm.achat([system_prompt, user_prompt])

        content = getattr(response.message, "content", None) or getattr(response, "message", None)
        if content is None:
            raise ValueError("LLM did not return any content")

        extracted_intents = {}
        try:
            cleaned = content.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`")
                if cleaned.lower().startswith("json"):
                    cleaned = cleaned[4:]

            extracted_intents = json.loads(cleaned)
        except Exception:
            extracted_intents = {"raw_response": content}

        return IntentOut(message=intent.message, intent_names=intent.intent_names, extracted_intents=extracted_intents)
