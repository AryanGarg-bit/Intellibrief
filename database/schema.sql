-- ==============================================================================
-- IntelliBrief: PostgreSQL / Supabase Schema (PRD Section 10)
-- 4 Core Tables: users, user_preferences, news_articles, daily_news_deliveries
-- ==============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ------------------------------------------------------------------------------
-- 1. USERS TABLE
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    subscription_status TEXT NOT NULL DEFAULT 'active' CHECK (subscription_status IN ('active', 'unsubscribed', 'pending')),
    quiz_completed BOOLEAN NOT NULL DEFAULT false,
    timezone TEXT NOT NULL DEFAULT 'Asia/Kolkata',
    consent_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_status_quiz ON public.users(subscription_status, quiz_completed);

-- ------------------------------------------------------------------------------
-- 2. USER PREFERENCES TABLE
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    category TEXT NOT NULL CHECK (category IN ('Finance', 'Technology')),
    topic_id TEXT NOT NULL,
    display_name TEXT NOT NULL,
    keywords TEXT[] DEFAULT '{}'::text[],
    interest_score INTEGER NOT NULL CHECK (interest_score BETWEEN 1 AND 10),
    source TEXT NOT NULL DEFAULT 'quiz' CHECK (source IN ('quiz', 'user_edit')),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    CONSTRAINT uq_user_topic UNIQUE (user_id, topic_id)
);

CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON public.user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_category ON public.user_preferences(category);

-- ------------------------------------------------------------------------------
-- 3. NEWS ARTICLES TABLE (Shared General Intelligence Pool)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.news_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL UNIQUE,
    published_at TIMESTAMPTZ NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    category TEXT NOT NULL CHECK (category IN ('Finance', 'Technology')),
    region TEXT NOT NULL DEFAULT 'Global' CHECK (region IN ('India', 'Global')),
    topic_ids TEXT[] DEFAULT '{}'::text[],
    entities TEXT[] DEFAULT '{}'::text[],
    content_excerpt TEXT,
    summary TEXT,
    why_it_matters TEXT,
    impact_analysis TEXT,
    outlook TEXT,
    importance_score NUMERIC(5, 2) DEFAULT 0.0,
    relevance_score NUMERIC(5, 2) DEFAULT 0.0,
    content_hash TEXT,
    event_key TEXT,
    source_quality NUMERIC(5, 2) DEFAULT 5.0,
    evidence_refs JSONB DEFAULT '[]'::jsonb,
    processing_status TEXT NOT NULL DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processed', 'failed', 'quarantined')),
    error_code TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_news_articles_published_at ON public.news_articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_articles_cat_reg ON public.news_articles(category, region);
CREATE INDEX IF NOT EXISTS idx_news_articles_status ON public.news_articles(processing_status);
CREATE INDEX IF NOT EXISTS idx_news_articles_event_key ON public.news_articles(event_key);

-- ------------------------------------------------------------------------------
-- 4. DAILY NEWS DELIVERIES TABLE
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.daily_news_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    report_date DATE NOT NULL,
    article_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    report_payload JSONB,
    profile_version TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'sent', 'retrying', 'failed', 'skipped', 'partial')),
    provider_message_id TEXT,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    idempotency_key TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    sent_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_deliveries_user_date ON public.daily_news_deliveries(user_id, report_date);
CREATE INDEX IF NOT EXISTS idx_deliveries_status ON public.daily_news_deliveries(status);

-- ------------------------------------------------------------------------------
-- AUTO-UPDATE updated_at TRIGGER FUNCTION
-- ------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_users_updated_at ON public.users;
CREATE TRIGGER set_users_updated_at
BEFORE UPDATE ON public.users
FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

DROP TRIGGER IF EXISTS set_user_preferences_updated_at ON public.user_preferences;
CREATE TRIGGER set_user_preferences_updated_at
BEFORE UPDATE ON public.user_preferences
FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

-- ------------------------------------------------------------------------------
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ------------------------------------------------------------------------------
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.news_articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_news_deliveries ENABLE ROW LEVEL SECURITY;

-- By default, backend service role bypasses RLS and handles pipeline jobs.
-- Allow read access to articles for authenticated frontend users:
CREATE POLICY "Allow public read access to processed news articles"
    ON public.news_articles FOR SELECT
    USING (processing_status = 'processed');
