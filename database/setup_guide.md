# Supabase Database Setup Guide

Follow these quick steps to set up your PostgreSQL database in Supabase for IntelliBrief:

### Step 1: Create a Free Supabase Project
1. Go to [https://supabase.com](https://supabase.com) and log in or create a free account.
2. Click **New Project**.
3. Choose an organization, enter a name (e.g. `intellibrief`), set a strong database password, and choose a region close to your users (e.g. `South Asia (Mumbai)`).
4. Wait 1-2 minutes for the database to provision.

### Step 2: Apply the Schema SQL
1. In your Supabase Dashboard, click on **SQL Editor** in the left sidebar.
2. Click **New query**.
3. Open the file [`database/schema.sql`](file:///c:/Users/Aryan/Desktop/IntelliBrief/database/schema.sql) in this repository.
4. Copy the entire contents and paste it into the Supabase SQL editor.
5. Click **Run** (or press `Ctrl+Enter`).
6. You should see `Success. No rows returned`.

### Step 3: Verify the Tables
1. Click on **Table Editor** in the left sidebar.
2. Verify that the following 4 tables exist:
   - `users`
   - `user_preferences`
   - `news_articles`
   - `daily_news_deliveries`

### Step 4: Get Your API Credentials
1. Go to **Project Settings** (gear icon) -> **API**.
2. Find the following values:
   - **Project URL**: Copy and set as `SUPABASE_URL` in your `.env` file.
   - **Project API Keys**:
     - `anon` `public`: Set as `SUPABASE_ANON_KEY` in `.env`.
     - `service_role` `secret`: Set as `SUPABASE_SERVICE_ROLE_KEY` in `.env` (Keep this strictly private; backend only).
