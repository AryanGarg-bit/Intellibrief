"""Taxonomy of stable topics for Finance and Technology."""

from typing import Dict, List, Optional
from pydantic import BaseModel


class TopicDefinition(BaseModel):
    topic_id: str
    display_name: str
    category: str  # "Finance" or "Technology"
    keywords: List[str]


# Stable, predefined topic registry
TAXONOMY: Dict[str, TopicDefinition] = {
    # --- FINANCE ---
    "indian_equities": TopicDefinition(
        topic_id="indian_equities",
        display_name="Indian Equities & Markets",
        category="Finance",
        keywords=["nifty", "sensex", "bse", "nse", "sebi", "dalal street", "india stocks"],
    ),
    "global_macro": TopicDefinition(
        topic_id="global_macro",
        display_name="Global Macroeconomics & Central Banks",
        category="Finance",
        keywords=["inflation", "federal reserve", "interest rates", "gdp", "recession", "ecb", "rbi"],
    ),
    "banking_fintech": TopicDefinition(
        topic_id="banking_fintech",
        display_name="Banking & FinTech",
        category="Finance",
        keywords=["upi", "payments", "neobank", "lending", "credit", "fintech", "banking"],
    ),
    "company_earnings": TopicDefinition(
        topic_id="company_earnings",
        display_name="Corporate Earnings & M&A",
        category="Finance",
        keywords=["revenue", "earnings", "quarterly results", "acquisition", "merger", "profit"],
    ),
    "commodities_crypto": TopicDefinition(
        topic_id="commodities_crypto",
        display_name="Commodities & Digital Assets",
        category="Finance",
        keywords=["crude oil", "gold", "bitcoin", "crypto", "currency", "forex"],
    ),

    # --- TECHNOLOGY ---
    "ai_ml_research": TopicDefinition(
        topic_id="ai_ml_research",
        display_name="AI Models & Research",
        category="Technology",
        keywords=["llm", "deep learning", "neural network", "openai", "gemini", "anthropic", "benchmark"],
    ),
    "ai_products": TopicDefinition(
        topic_id="ai_products",
        display_name="AI Products & Applications",
        category="Technology",
        keywords=["generative ai", "copilot", "chatgpt", "agents", "ai app", "enterprise ai"],
    ),
    "semiconductors": TopicDefinition(
        topic_id="semiconductors",
        display_name="Semiconductors & Hardware",
        category="Technology",
        keywords=["nvidia", "tsmc", "chips", "foundry", "gpu", "intel", "amd", "semiconductor"],
    ),
    "cloud_infra": TopicDefinition(
        topic_id="cloud_infra",
        display_name="Cloud & Data Centers",
        category="Technology",
        keywords=["aws", "azure", "google cloud", "datacenter", "server", "kubernetes", "cloud"],
    ),
    "cybersecurity": TopicDefinition(
        topic_id="cybersecurity",
        display_name="Cybersecurity & Privacy",
        category="Technology",
        keywords=["ransomware", "data breach", "vulnerability", "malware", "zero-day", "security"],
    ),
    "software_dev": TopicDefinition(
        topic_id="software_dev",
        display_name="Software Engineering & Dev Tools",
        category="Technology",
        keywords=["github", "open source", "developer", "api", "programming", "python", "javascript"],
    ),
}


def get_topic(topic_id: str) -> Optional[TopicDefinition]:
    """Retrieve a topic definition by ID, or None if not found."""
    return TAXONOMY.get(topic_id)


def get_all_topics() -> List[TopicDefinition]:
    """Retrieve all available taxonomy topics."""
    return list(TAXONOMY.values())
