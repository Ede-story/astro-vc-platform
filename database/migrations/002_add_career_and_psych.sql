-- Migration: Add career, psych_scores, and related fields
-- Version: 002
-- Date: 2025-11-29
-- Description: Adds career field, psychometric test scores, and private analysis table

-- ==========================================
-- ALTER profiles table - Add new columns
-- ==========================================

-- Add username column if not exists
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS username TEXT UNIQUE;

-- Add bio column if not exists
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS bio TEXT;

-- Add career column
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS career TEXT;

-- Add psych_scores column (JSONB for flexible storage)
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS psych_scores JSONB DEFAULT '{}';

-- Add psych completion timestamp
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS psych_completed_at TIMESTAMPTZ;

-- Add seeking/offerings arrays
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS seeking TEXT[] DEFAULT '{}';

ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS offerings TEXT[] DEFAULT '{}';

-- Add onboarding status
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT FALSE;

-- Add username index
CREATE INDEX IF NOT EXISTS idx_profiles_username ON public.profiles(username);

-- ==========================================
-- CREATE private_analysis table
-- ==========================================

CREATE TABLE IF NOT EXISTS public.private_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,

    -- AI-generated content (populated by LLM analysis)
    personality_summary TEXT,
    talent_analysis TEXT,
    career_advice TEXT,
    ideal_partner TEXT,
    life_areas JSONB,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_private_analysis_user_id ON public.private_analysis(user_id);

-- ==========================================
-- RLS Policies for private_analysis
-- ==========================================

ALTER TABLE public.private_analysis ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (for re-running migration)
DROP POLICY IF EXISTS "Users can view own analysis" ON public.private_analysis;
DROP POLICY IF EXISTS "Users can insert own analysis" ON public.private_analysis;
DROP POLICY IF EXISTS "Users can update own analysis" ON public.private_analysis;

-- Create policies
CREATE POLICY "Users can view own analysis"
ON public.private_analysis FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own analysis"
ON public.private_analysis FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own analysis"
ON public.private_analysis FOR UPDATE
USING (auth.uid() = user_id);

-- ==========================================
-- Grants
-- ==========================================

GRANT ALL ON public.private_analysis TO authenticated;

-- ==========================================
-- Comments
-- ==========================================

COMMENT ON COLUMN public.profiles.career IS 'User career/occupation description';
COMMENT ON COLUMN public.profiles.psych_scores IS 'Psychometric test results (10 dimensions, 0-100)';
COMMENT ON COLUMN public.profiles.psych_completed_at IS 'When user completed the psychometric test';
COMMENT ON COLUMN public.profiles.seeking IS 'What user is looking for (business, romance, etc)';
COMMENT ON COLUMN public.profiles.offerings IS 'What user offers (expertise, mentoring, etc)';
COMMENT ON TABLE public.private_analysis IS 'AI-generated personality analysis (private to user)';
