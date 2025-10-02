from fastapi import FastAPI
from dotenv import load_dotenv

from core.models.intents import IntentIn, IntentOut
from core.services.intent_service import IntentService

load_dotenv()
app = FastAPI()


@app.post("/api/v1/intents")
async def extract_intents(intent: IntentIn) -> IntentOut:
    intent_service = IntentService()
    return await intent_service.extract_intents(intent)
