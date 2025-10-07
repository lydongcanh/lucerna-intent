from pydantic import BaseModel


class IntentIn(BaseModel):
    message: str

class IntentOut(BaseModel):
    extracted_intents: dict[str, str]