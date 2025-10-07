import difflib
from typing import Dict, Any

class IntentCanonicalizer:
    """
    Maps LLM-extracted intents to canonical taxonomy values.
    """

    ENTITY_PRIMARY = [
        "document", "file", "data_room", "deal", "user", "participant",
        "report", "workflow", "system", "policy", "question",
    ]

    CATEGORY = [
        "document_management", "data_room_management", "user_management",
        "workflow_automation", "analytics_reporting", "security_compliance",
        "integration", "product_comparison", "pricing_billing", "general_information",
    ]

    FEATURE_FOCUS = [
        "summarization", "comparison", "search", "upload", "sharing", "permissions",
        "notifications", "audit_trail", "export", "translation", "recommendation",
        "classification", "generation",
    ]

    PURPOSE = [
        "learn", "analyze", "compare", "decide", "summarize", "organize",
        "understand", "improve", "review",
    ]

    DECISION_CONTEXT = [
        "deal_preparation", "m_a_project", "due_diligence", "compliance_check",
        "internal_review", "client_meeting", "training", "onboarding",
        "daily_operations", "unknown",
    ]

    ACTION_INTENT = [
        "summarize", "compare", "explain", "analyze", "classify", "recommend",
        "translate", "extract", "generate", "search", "create", "update", "delete",
    ]

    TONE = ["neutral", "curious", "frustrated", "positive", "negative", "urgent"]

    CANONICAL_INTENTS = {
        "entity_primary": ENTITY_PRIMARY,
        "category": CATEGORY,
        "feature_focus": FEATURE_FOCUS,
        "purpose": PURPOSE,
        "decision_context": DECISION_CONTEXT,
        "action_intent": ACTION_INTENT,
        "tone": TONE,
    }

    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold

    def canonicalize_intent(self, intent_name: str, extracted_value: str) -> str:
        """Canonicalize a single extracted intent value."""

        if intent_name not in self.CANONICAL_INTENTS or not extracted_value:
            return extracted_value

        canonical_options = self.CANONICAL_INTENTS[intent_name]
        matches = difflib.get_close_matches(
            extracted_value.lower(), 
            [option.lower() for option in canonical_options], 
            n=1, 
            cutoff=self.similarity_threshold
        )

        print(f"Canonicalizing intent '{intent_name}': extracted '{extracted_value}' -> matched '{matches[0] if matches else ''}'")

        return matches[0] if matches else extracted_value
    
    def canonicalize_intents(self, extracted_intents: Dict[str, Any]) -> Dict[str, str]:
        """Canonicalize a dictionary of extracted intents."""

        canonicalized = {}

        for intent_name, extracted_value in extracted_intents.items():
            if isinstance(extracted_value, str):
                canonicalized[intent_name] = self.canonicalize_intent(intent_name, extracted_value)
            else:
                canonicalized[intent_name] = None

        return canonicalized
