"""
Local pipeline execution script.
Run this script to simulate a complete daily cycle:
1. Subscribes a demo user
2. Completes their preference quiz
3. Runs General Intelligence news collection (Layer A)
4. Personalizes and renders their 5 Finance + 5 Tech briefing (Layer B)
5. Saves an HTML preview to 'email_preview.html' for instant viewing
"""

import os
import sys
from pathlib import Path

# Add project root to python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas import SubscribeRequest, QuizSubmissionRequest, QuizAnswer
from app.routes.subscription import subscribe, complete_quiz
from app.jobs.daily_pipeline import run_daily_pipeline
from app.general_intelligence.rss_client import RawFeedItem
from app.repositories.users_repository import users_repo
from app.repositories.articles_repository import articles_repo
from app.repositories.preferences_repository import preferences_repo
from app.personalization.select_stories import select_daily_stories
from app.reporting.render_email import render_email
from app.utils.time import today_ist_date_string


def main():
    print("=" * 60)
    print("📰 INTELLIBRIEF — LOCAL PIPELINE SIMULATION")
    print("=" * 60)

    # 1. Subscribe a test user
    test_email = "investor.demo@example.com"
    print(f"\n1. Subscribing user: {test_email}")
    sub_res = subscribe(SubscribeRequest(email=test_email))
    user_id = sub_res.user_id
    print(f"   ✓ User ID: {user_id}")

    # 2. Complete Quiz
    print("\n2. Submitting Onboarding Quiz answers...")
    answers = [
        QuizAnswer(
            question_id="q_fin_sectors",
            selected_topic_ids=["indian_equities", "banking_fintech"],
            interest_level=9,
        ),
        QuizAnswer(
            question_id="q_tech_sectors",
            selected_topic_ids=["semiconductors", "ai_products"],
            interest_level=8,
        ),
    ]
    quiz_res = complete_quiz(QuizSubmissionRequest(user_id=user_id, answers=answers))
    print(f"   ✓ Saved {len(quiz_res.preferences)} preference topics:")
    for pref in quiz_res.preferences:
        print(f"     • {pref.display_name} ({pref.category}): Score {pref.interest_score}/10")

    # 3. Feed candidate items (Layer A simulation)
    print("\n3. Ingesting candidate news pool (Layer A)...")
    sample_news = [
        # Finance stories
        RawFeedItem(
            title="RBI maintains benchmark repo rate at 6.50% amidst steady growth",
            link="https://economictimes.example.com/rbi-rates-held",
            published=None,
            summary="Reserve Bank of India Governor announced policy stance following the Monetary Policy Committee meeting in Mumbai.",
            source_name="Economic Times",
        ),
        RawFeedItem(
            title="Nifty 50 crosses 24,500 record high powered by banking and auto stocks",
            link="https://livemint.example.com/nifty-record-high",
            published=None,
            summary="Indian equities touched fresh record highs on Dalal Street as institutional foreign investors resumed purchases.",
            source_name="Livemint",
        ),
        RawFeedItem(
            title="FinTech startup raises $45M Series B for UPI credit expansion",
            link="https://inc42.example.com/fintech-upi-round",
            published=None,
            summary="Digital lending platform closes growth financing to expand credit lines on UPI rail for merchants.",
            source_name="Inc42",
        ),
        RawFeedItem(
            title="US Federal Reserve signals cautious approach on interest rate trajectory",
            link="https://reuters.example.com/fed-policy-update",
            published=None,
            summary="Chair Jerome Powell emphasized inflation data dependence at the latest economic symposium.",
            source_name="Reuters",
        ),
        RawFeedItem(
            title="HDFC Bank reports 16% YoY growth in net profit for Q2",
            link="https://moneycontrol.example.com/hdfc-earnings",
            published=None,
            summary="India's largest private lender reported strong asset quality and steady net interest margins.",
            source_name="Moneycontrol",
        ),

        # Technology stories
        RawFeedItem(
            title="NVIDIA and TSMC announce mass production of next-generation AI accelerators",
            link="https://techcrunch.example.com/nvidia-tsmc-ai-silicon",
            published=None,
            summary="New custom chip architecture promises 3x energy efficiency improvements for large language model inference.",
            source_name="TechCrunch",
        ),
        RawFeedItem(
            title="Enterprise AI adoption accelerates as generative tools reach 40% of Fortune 500",
            link="https://theverge.example.com/enterprise-ai-growth",
            published=None,
            summary="Surveys show rapid integration of coding assistants and automated workflow agents across enterprises.",
            source_name="The Verge",
        ),
        RawFeedItem(
            title="Global semiconductor foundry capacity expands with new fab in Gujarat",
            link="https://et.example.com/gujarat-semiconductor-fab",
            published=None,
            summary="Construction begins on landmark wafer fabrication facility supported by India Semiconductor Mission.",
            source_name="Economic Times",
        ),
        RawFeedItem(
            title="Cybersecurity researchers uncover zero-day vulnerability in popular cloud gateway",
            link="https://wired.example.com/cloud-zero-day",
            published=None,
            summary="Security patches issued globally following detection of an authentication bypass vulnerability.",
            source_name="Wired",
        ),
        RawFeedItem(
            title="Google and Anthropic announce new safety evaluation benchmarks for reasoning models",
            link="https://techcrunch.example.com/ai-safety-benchmarks",
            published=None,
            summary="Standardized evaluation suites aim to measure frontier model alignment and hallucination rates.",
            source_name="TechCrunch",
        ),
    ]

    report_date = today_ist_date_string()
    summary = run_daily_pipeline(report_date=report_date, custom_feed_items=sample_news)
    print(f"   ✓ Layer A generated {summary['layer_a']['total_added']} candidate stories.")
    print(f"   ✓ Layer B delivered to {summary['layer_b']['sent']} subscribers.")

    # 4. Generate & Save HTML Preview
    user = users_repo.get_by_id(user_id)
    candidates = articles_repo.list_candidates(limit=50)
    user_prefs = preferences_repo.get_preferences(user_id)
    selection = select_daily_stories(candidates, user_prefs, target_per_category=5)

    subject, html_content, text_content = render_email(
        report_date=report_date,
        selection=selection,
        user_email=test_email,
        user_id=user_id,
    )

    preview_path = Path("email_preview.html")
    preview_path.write_text(html_content, encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"🎉 SUCCESS! Email briefing preview saved to: {preview_path.resolve()}")
    print("=" * 60)
    print("\n--- PLAIN-TEXT EMAIL PREVIEW ---")
    print(text_content[:800] + "\n...[truncated for brevity]...\n")


if __name__ == "__main__":
    main()
