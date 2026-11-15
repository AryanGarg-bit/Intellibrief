# PRODUCT REQUIREMENTS DOCUMENT
## AI Personalized Finance & Technology News Assistant (IntelliBrief)
**Version 1.0** | **Status: In Development** | **Date: 14 November 2026**

---

### 0. Instructions
Treat this PRD as the source of truth. Implement only Version 1 scope; do not add speculative features.
Build the application code, tests, documentation, and local configuration templates. Keep modules small, single-purpose, and easy to understand.
Do NOT create, provision, migrate, configure, or modify external infrastructure/accounts: Supabase project/database, email provider account/domain/DNS, API keys, hosting, scheduler configuration, or production secrets.
For external components, provide the user with clear step-by-step setup instructions, SQL/schema files, dashboard instructions, required environment variables, and verification steps. Stop and ask the user to perform external setup. Never claim an external component is configured unless verified.
Do not put secrets in source code, frontend bundles, logs, or committed files. Create .env.example only; never create a real .env with guessed values.
Before implementing, present a concise plan and identify any genuine ambiguity. Then implement incrementally, run tests, report outcomes, and preserve this PRD's acceptance criteria.
Do not silently relax validation or fabricate news to fill a report. Fail safely and make partial-data status visible.

---

### 1. Product Overview
Build a personalizable AI news assistant. A visitor subscribes for free using an email address, completes a short finance/technology preference quiz, and receives an automated email every day at 07:00 Asia/Kolkata containing exactly five Finance stories and five Technology stories when sufficient qualifying news exists. Stories can be India-focused or global. The website also provides a useful dashboard for reading, exploring, and managing the user's news preferences.
The product is intentionally a reliable, understandable MVP—not an industry-grade platform delivered in one go. Correctness, modularity, tests, edge-case handling, and graceful fallbacks take priority over feature count.

---

### 2. Goals and Non-Goals
#### 2.1 Goals
- Deliver 10 useful stories daily: 5 Finance and 5 Technology, selected for significance and novelty—not merely recency or generic aggregation.
- Research and analyze news once in a shared General Intelligence layer; personalize selection separately for each subscriber.
- Use quiz-derived structured preferences to improve relevance.
- Provide a dashboard with real user value: today's briefing, news exploration, preference management, and report history.
- Use focused Python modules with minimal, understandable functions and explicit data contracts.
- Make daily execution observable, retry-safe, idempotent, and resilient to source/API/model/email failures.
- Keep all stories traceable to credible sources and original article URLs.

#### 2.2 Non-Goals for Version 1
- No stock-price prediction, investment advice, trading signals, or guaranteed future outlook.
- No autonomous financial transactions or portfolio management.
- No complex multi-agent framework; use one pipeline with two intelligence layers.
- No vector database/RAG requirement, microservices, Kubernetes, or elaborate analytics.
- No WhatsApp delivery in V1; email is the confirmed delivery channel. Architecture may allow later addition.
- No paid subscription/billing; subscription is free.
- No user-generated posts or social feed.
- No promise to reproduce paywalled article text. Respect source/provider terms and access restrictions.

---

### 3. Confirmed Requirements
| Decision | Requirement |
|---|---|
| Audience | Free subscribers; initial product is personal/small-scale, architecture should not assume one hard-coded user. |
| Coverage | India + Global; no separate region quota. |
| Categories | Finance and Technology. |
| Delivery | Automated email, daily at 07:00 IST (Asia/Kolkata). |
| Email content | 5 Finance + 5 Technology stories; total 10 when enough qualifying stories exist. |
| Personalization | 5–10 question onboarding quiz; derive explicit interests/keywords and scores. |
| Website | Subscription landing page, quiz, personalized intelligence dashboard, news explorer, preference management, archive. |
| AI approach | Two layers: shared General News Intelligence and per-user Personalization Intelligence. |
| Reliability | Edge-case testing, safe fallbacks, retry policy, idempotency, logs, no invented news. |
| External setup | IDE guides the user; it must not create/configure external accounts or infrastructure. |

---

### 4. Database Design (Initial 4 Tables)
1. **`users`**: UUID `id`, `email`, `subscription_status`, `quiz_completed`, `timezone`, `created_at`, `updated_at`, `consent_at`.
2. **`user_preferences`**: UUID `id`, `user_id`, `category`, `topic_id`, `display_name`, `keywords`, `interest_score` (1-10), `source`, `updated_at`.
3. **`news_articles`**: UUID `id`, `title`, `source_name`, `source_url`, `published_at`, `fetched_at`, `category`, `region`, `topic_ids`, `entities`, `content_excerpt`, `summary`, `why_it_matters`, `impact_analysis`, `outlook`, `importance_score`, `relevance_score`, `content_hash`, `event_key`, `source_quality`, `evidence_refs`, `processing_status`, `error_code`.
4. **`daily_news_deliveries`**: UUID `id`, `user_id`, `report_date`, `article_ids`, `report_payload`, `profile_version`, `status`, `provider_message_id`, `attempt_count`, `last_error`, `created_at`, `sent_at`, `idempotency_key`.
