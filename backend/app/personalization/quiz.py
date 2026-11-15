"""Onboarding quiz questions and validation logic."""

from typing import List, Dict, Any
from app.personalization.taxonomy import TAXONOMY


# Defined 6 concise questions for finance and tech onboarding
QUIZ_QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": "q_geo",
        "question": "Which markets are you most interested in following?",
        "options": [
            {"id": "geo_india", "label": "India-focused markets & companies", "topics": ["indian_equities", "banking_fintech"]},
            {"id": "geo_global", "label": "Global markets & Wall Street", "topics": ["global_macro", "company_earnings"]},
            {"id": "geo_both", "label": "Both India and Global", "topics": ["indian_equities", "global_macro"]},
        ],
    },
    {
        "id": "q_fin_sectors",
        "question": "Which financial sectors matter most to you?",
        "options": [
            {"id": "indian_equities", "label": "Indian Stock Market & Indices", "topics": ["indian_equities"]},
            {"id": "global_macro", "label": "Macroeconomics & Central Banks (Fed, RBI)", "topics": ["global_macro"]},
            {"id": "banking_fintech", "label": "FinTech, Payments & Digital Banking", "topics": ["banking_fintech"]},
            {"id": "company_earnings", "label": "Corporate Earnings, Deals & M&A", "topics": ["company_earnings"]},
            {"id": "commodities_crypto", "label": "Commodities, Forex & Crypto", "topics": ["commodities_crypto"]},
        ],
    },
    {
        "id": "q_ai_interest",
        "question": "How closely do you track Artificial Intelligence developments?",
        "options": [
            {"id": "ai_heavy", "label": "Deeply - AI research, frontier models & technical breakthroughs", "topics": ["ai_ml_research", "ai_products"]},
            {"id": "ai_practical", "label": "Practically - AI products, apps & business tools", "topics": ["ai_products"]},
            {"id": "ai_general", "label": "High level - Just major industry shifts", "topics": ["ai_products"]},
        ],
    },
    {
        "id": "q_tech_sectors",
        "question": "Which tech hardware & infrastructure areas interest you?",
        "options": [
            {"id": "semiconductors", "label": "Semiconductors & Chip Hardware (NVIDIA, TSMC)", "topics": ["semiconductors"]},
            {"id": "cloud_infra", "label": "Cloud Platforms & Data Centers", "topics": ["cloud_infra"]},
            {"id": "cybersecurity", "label": "Cybersecurity & Threat Defense", "topics": ["cybersecurity"]},
            {"id": "software_dev", "label": "Software Engineering & Developer Tools", "topics": ["software_dev"]},
        ],
    },
]


def get_quiz_questions() -> List[Dict[str, Any]]:
    """Return all onboarding questions for the quiz UI."""
    return QUIZ_QUESTIONS


def validate_answers(answers: list) -> bool:
    """Validate that answers list is non-empty and has selected options."""
    if not answers or len(answers) < 1:
        return False
    return True
