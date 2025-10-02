from pydantic import BaseModel


class IntentIn(BaseModel):
    message: str
    intent_names: list[str]


class IntentOut(IntentIn):
    extracted_intents: dict[str, str]