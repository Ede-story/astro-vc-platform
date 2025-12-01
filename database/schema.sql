-- StarMeet Database Schema
-- Version: 1.0
-- Purpose: User profiles, vedic charts, compatibility matching

-- ==========================================
-- EXTENSIONS
-- ==========================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==========================================
-- SUPABASE AUTH SCHEMA (Required for GoTrue)
-- ==========================================

CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS _realtime;

-- Auth roles for Row Level Security
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'anon') THEN
        CREATE ROLE anon NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'authenticated') THEN
        CREATE ROLE authenticated NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'service_role') THEN
        CREATE ROLE service_role NOLOGIN;
    END IF;
END
$$;

-- Grant permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated, service_role;

-- Auth users table (created by GoTrue, but we need structure)
CREATE TABLE IF NOT EXISTS auth.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    encrypted_password VARCHAR(255),
    email_confirmed_at TIMESTAMPTZ,
    invited_at TIMESTAMPTZ,
    confirmation_token VARCHAR(255),
    confirmation_sent_at TIMESTAMPTZ,
    recovery_token VARCHAR(255),
    recovery_sent_at TIMESTAMPTZ,
    email_change_token_new VARCHAR(255),
    email_change VARCHAR(255),
    email_change_sent_at TIMESTAMPTZ,
    last_sign_in_at TIMESTAMPTZ,
    raw_app_meta_data JSONB DEFAULT '{}'::jsonb,
    raw_user_meta_data JSONB DEFAULT '{}'::jsonb,
    is_super_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    phone VARCHAR(255),
    phone_confirmed_at TIMESTAMPTZ,
    phone_change VARCHAR(255),
    phone_change_token VARCHAR(255),
    phone_change_sent_at TIMESTAMPTZ,
    confirmed_at TIMESTAMPTZ,
    email_change_token_current VARCHAR(255),
    email_change_confirm_status SMALLINT,
    banned_until TIMESTAMPTZ,
    reauthentication_token VARCHAR(255),
    reauthentication_sent_at TIMESTAMPTZ,
    is_sso_user BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMPTZ
);

-- ==========================================
-- PROFILES TABLE
-- ==========================================

CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Basic Info
    name TEXT NOT NULL,
    username TEXT UNIQUE,
    bio TEXT,
    career TEXT,
    avatar_url TEXT,

    -- Birth Data
    birth_date DATE NOT NULL,
    birth_time TIME,
    birth_city TEXT,
    birth_latitude FLOAT,
    birth_longitude FLOAT,
    birth_timezone FLOAT,

    -- Ayanamsa System
    ayanamsa TEXT DEFAULT 'raman' CHECK (ayanamsa IN ('raman', 'lahiri', 'krishnamurti')),

    -- Calculated Vedic Chart (all 60 vargas stored as JSONB)
    digital_twin JSONB,

    -- Psychometric Test Results
    psych_scores JSONB DEFAULT '{}',
    psych_completed_at TIMESTAMPTZ,

    -- Interests/Goals
    seeking TEXT[] DEFAULT '{}',
    offerings TEXT[] DEFAULT '{}',

    -- Onboarding Status
    onboarding_completed BOOLEAN DEFAULT FALSE,

    -- Metadata
    is_primary BOOLEAN DEFAULT FALSE,  -- User's main profile
    is_public BOOLEAN DEFAULT FALSE,   -- Visible to others
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for profiles
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON public.profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_profiles_username ON public.profiles(username);
CREATE INDEX IF NOT EXISTS idx_profiles_created_at ON public.profiles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_profiles_is_public ON public.profiles(is_public) WHERE is_public = TRUE;

-- ==========================================
-- PRIVATE ANALYSIS TABLE (AI-generated insights)
-- ==========================================

CREATE TABLE IF NOT EXISTS public.private_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
-- COMPATIBILITY CACHE TABLE
-- ==========================================

CREATE TABLE IF NOT EXISTS public.compatibility_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_a_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    profile_b_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,

    -- Compatibility Scores
    overall_score FLOAT,
    kuta_score JSONB,          -- Ashtakuta matching details
    dasha_compatibility JSONB,  -- Dasha period compatibility
    house_overlay JSONB,       -- House placement overlay

    -- Metadata
    calculated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure unique pair (regardless of order)
    CONSTRAINT unique_profile_pair UNIQUE (profile_a_id, profile_b_id),
    CONSTRAINT ordered_profile_pair CHECK (profile_a_id < profile_b_id)
);

CREATE INDEX IF NOT EXISTS idx_compatibility_profile_a ON public.compatibility_cache(profile_a_id);
CREATE INDEX IF NOT EXISTS idx_compatibility_profile_b ON public.compatibility_cache(profile_b_id);

-- ==========================================
-- MATCHES TABLE (Future: Social Features)
-- ==========================================

CREATE TABLE IF NOT EXISTS public.matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_a_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    user_b_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Match Status
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected', 'blocked')),

    -- Who initiated
    initiated_by UUID REFERENCES auth.users(id),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure unique pair
    CONSTRAINT unique_match_pair UNIQUE (user_a_id, user_b_id),
    CONSTRAINT ordered_match_pair CHECK (user_a_id < user_b_id)
);

CREATE INDEX IF NOT EXISTS idx_matches_user_a ON public.matches(user_a_id);
CREATE INDEX IF NOT EXISTS idx_matches_user_b ON public.matches(user_b_id);
CREATE INDEX IF NOT EXISTS idx_matches_status ON public.matches(status);

-- ==========================================
-- MESSAGES TABLE (Future: Social Features)
-- ==========================================

CREATE TABLE IF NOT EXISTS public.messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    match_id UUID NOT NULL REFERENCES public.matches(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Content
    content TEXT NOT NULL,

    -- Read status
    read_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_match_id ON public.messages(match_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON public.messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON public.messages(created_at DESC);

-- ==========================================
-- ROW LEVEL SECURITY (RLS)
-- ==========================================

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.private_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.compatibility_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

-- Profiles: Users can CRUD their own profiles
CREATE POLICY "Users can view own profiles"
    ON public.profiles FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can view public profiles"
    ON public.profiles FOR SELECT
    USING (is_public = TRUE);

CREATE POLICY "Users can insert own profiles"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own profiles"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own profiles"
    ON public.profiles FOR DELETE
    USING (auth.uid() = user_id);

-- Private Analysis: Only owner can access their analysis
CREATE POLICY "Users can view own analysis"
    ON public.private_analysis FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own analysis"
    ON public.private_analysis FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own analysis"
    ON public.private_analysis FOR UPDATE
    USING (auth.uid() = user_id);

-- Compatibility: Users can view compatibility involving their profiles
CREATE POLICY "Users can view own compatibility"
    ON public.compatibility_cache FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.user_id = auth.uid()
            AND (p.id = profile_a_id OR p.id = profile_b_id)
        )
    );

-- Matches: Users can view their own matches
CREATE POLICY "Users can view own matches"
    ON public.matches FOR SELECT
    USING (auth.uid() = user_a_id OR auth.uid() = user_b_id);

CREATE POLICY "Users can create matches"
    ON public.matches FOR INSERT
    WITH CHECK (auth.uid() = initiated_by);

CREATE POLICY "Users can update own matches"
    ON public.matches FOR UPDATE
    USING (auth.uid() = user_a_id OR auth.uid() = user_b_id);

-- Messages: Users can view messages in their matches
CREATE POLICY "Users can view messages in own matches"
    ON public.messages FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.matches m
            WHERE m.id = match_id
            AND (m.user_a_id = auth.uid() OR m.user_b_id = auth.uid())
        )
    );

CREATE POLICY "Users can send messages in own matches"
    ON public.messages FOR INSERT
    WITH CHECK (
        auth.uid() = sender_id AND
        EXISTS (
            SELECT 1 FROM public.matches m
            WHERE m.id = match_id
            AND m.status = 'accepted'
            AND (m.user_a_id = auth.uid() OR m.user_b_id = auth.uid())
        )
    );

-- ==========================================
-- FUNCTIONS
-- ==========================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER update_matches_updated_at
    BEFORE UPDATE ON public.matches
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- Helper function to get auth user id
CREATE OR REPLACE FUNCTION auth.uid()
RETURNS UUID AS $$
    SELECT COALESCE(
        current_setting('request.jwt.claim.sub', TRUE)::UUID,
        '00000000-0000-0000-0000-000000000000'::UUID
    );
$$ LANGUAGE sql STABLE;

-- ==========================================
-- INITIAL DATA (Optional test user for development)
-- ==========================================

-- Uncomment for development:
-- INSERT INTO auth.users (id, email, encrypted_password, email_confirmed_at)
-- VALUES (
--     'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
--     'test@star-meet.com',
--     crypt('test123', gen_salt('bf')),
--     NOW()
-- );

-- ==========================================
-- GRANT PERMISSIONS FOR WEB ACCESS
-- ==========================================

-- Anon can read public profiles
GRANT SELECT ON public.profiles TO anon;

-- Authenticated users have full access to their data
GRANT ALL ON public.profiles TO authenticated;
GRANT ALL ON public.private_analysis TO authenticated;
GRANT ALL ON public.compatibility_cache TO authenticated;
GRANT ALL ON public.matches TO authenticated;
GRANT ALL ON public.messages TO authenticated;

-- Service role has full access
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL TABLES IN SCHEMA auth TO service_role;

COMMENT ON TABLE public.profiles IS 'User birth profiles with calculated vedic charts';
COMMENT ON TABLE public.compatibility_cache IS 'Pre-calculated compatibility scores between profiles';
COMMENT ON TABLE public.matches IS 'User connections/matches';
COMMENT ON TABLE public.messages IS 'Direct messages between matched users';
