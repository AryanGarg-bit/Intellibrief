"""News classification: Category, Region, and Topic tagging."""

import re
from typing import List, Tuple
from app.personalization.taxonomy import TAXONOMY

# India-specific keywords for region detection
INDIA_KEYWORDS = {
    "india", "indian", "delhi", "mumbai", "bengaluru", "bangalore",
    "rbi", "sebi", "nifty", "sensex", "bse", "nse", "dalal street",
    "rupee", "isro", "iit", "upi",
}

# Broad finance keywords
FINANCE_KEYWORDS = {
    "stock", "market", "shares", "nasdaq", "dow", "sp500", "economy",
    "inflation", "bank", "banking", "fed", "federal reserve", "treasury",
    "dividend", "investor", "revenue", "profit", "earnings", "crypto",
    "bitcoin", "fintech", "gdp", "yield", "bond", "fund", "venture",
}

# Broad technology keywords
TECH_KEYWORDS = {
    "ai", "artificial intelligence", "tech", "technology", "software",
    "hardware", "chip", "semiconductor", "cloud", "cybersecurity",
    "robotics", "nvidia", "apple", "google", "microsoft", "meta",
    "startup", "app", "algorithm", "model", "llm", "developer", "data",
}


def detect_region(text: str) -> str:
    """Detect whether article is India-focused or Global."""
    lower_text = text.lower()
    words = set(re.findall(r"\b[a-z]{3,}\b", lower_text))

    if words.intersection(INDIA_KEYWORDS):
        return "India"
    return "Global"


def classify_category_and_topics(title: str, excerpt: str) -> Tuple[str, List[str]]:
    """
    Classify article into Finance or Technology, and extract matched topic IDs.
    Returns (category, list_of_topic_ids).
    """
    combined_text = f"{title} {excerpt}".lower()
    words = set(re.findall(r"\b[a-z0-9_-]{2,}\b", combined_text))

    fin_score = len(words.intersection(FINANCE_KEYWORDS))
    tech_score = len(words.intersection(TECH_KEYWORDS))

    matched_topics: List[str] = []

    # Check each topic in the taxonomy
    for topic_id, topic_def in TAXONOMY.items():
        for kw in topic_def.keywords:
            if kw.lower() in combined_text:
                matched_topics.append(topic_id)
                if topic_def.category == "Finance":
                    fin_score += 2
                else:
                    tech_score += 2
                break

    # Determine category
    if fin_score >= tech_score:
        category = "Finance"
    else:
        category = "Technology"

    return category, matched_topics
