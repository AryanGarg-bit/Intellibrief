# IntelliBrief 📰

AI-Powered Personalized Finance & Technology News Assistant.

Delivers a curated, strictly factual briefing of **5 Finance stories + 5 Technology stories** directly to your inbox every morning at **07:00 IST**, personalized to your preferences via a fast onboarding quiz.

---

## 🚀 Quick Start (Local Development)

### 1. Requirements
- Python 3.11+
- Node.js 18+ (for frontend)

### 2. Backend Setup
1. Clone the repository and enter the directory:
   ```bash
   cd IntelliBrief
   ```
2. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the test suite:
   ```bash
   python -m pytest backend/tests
   ```
5. Start the backend development server:
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```
   Interactive API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 🗄️ Database Setup
See [`database/setup_guide.md`](database/setup_guide.md) for instructions on creating your free Supabase project and running the schema script [`database/schema.sql`](database/schema.sql).

---

## 📋 Architecture & Principles
- **Two-Layer Intelligence**: 
  - **Layer A (General News Intelligence)**: Scrapes, deduplicates, and summarizes candidate news once daily.
  - **Layer B (Personalization Intelligence)**: Scores and selects 5 Finance + 5 Tech stories per subscriber based on quiz preferences.
- **Strict Quality Rules**:
  - No fabricated or hallucinated news.
  - If fewer than 5 qualified stories exist, report explicit shortages (e.g., "3 of 5 stories available today").
  - Every story links to the original credible source URL.
  - Idempotent delivery to prevent duplicate emails.
