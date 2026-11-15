"""Data schemas and contracts using Pydantic."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


# ------------------------------------------------------------------------------
# Health & Status
# ------------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    timestamp: datetime


class ReadinessResponse(BaseModel):
    ready: bool
    supabase_configured: bool
    gemini_configured: bool
    resend_configured: bool


# ------------------------------------------------------------------------------
# Subscription & User
# ------------------------------------------------------------------------------
class SubscribeRequest(BaseModel):
    email: EmailStr


class SubscribeResponse(BaseModel):
    user_id: str
    email: str
    subscription_status: str
    quiz_completed: bool
    message: str


class UnsubscribeRequest(BaseModel):
    email: EmailStr


# ------------------------------------------------------------------------------
# Quiz & Preferences
# ------------------------------------------------------------------------------
class QuizAnswer(BaseModel):
    question_id: str
    selected_topic_ids: List[str] = Field(default_factory=list)
    interest_level: int = Field(default=7, ge=1, le=10)


class QuizSubmissionRequest(BaseModel):
    user_id: str
    answers: List[QuizAnswer]


class PreferenceItem(BaseModel):
    topic_id: str
    display_name: str
    category: str  # "Finance" or "Technology"
    interest_score: int = Field(ge=1, le=10)
    keywords: List[str] = Field(default_factory=list)


class UserPreferencesResponse(BaseModel):
    user_id: str
    preferences: List[PreferenceItem]


# ------------------------------------------------------------------------------
# News Articles & Reports
# ------------------------------------------------------------------------------
class ArticleItem(BaseModel):
    id: str
    title: str
    source_name: str
    source_url: str
    published_at: datetime
    category: str  # "Finance" or "Technology"
    region: str = "Global"  # "India" or "Global"
    summary: Optional[str] = None
    why_it_matters: Optional[str] = None
    impact_analysis: Optional[str] = None
    importance_score: float = 0.0


class DailyReportResponse(BaseModel):
    report_date: str
    executive_summary: str
    finance_stories: List[ArticleItem]
    technology_stories: List[ArticleItem]
    finance_count_note: Optional[str] = None
    tech_count_note: Optional[str] = None
