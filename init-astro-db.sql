-- StarMeet Astrology Database Initialization
-- This script runs once when PostgreSQL container starts for the first time
-- File: init-astro-db.sql

-- Create astro_db database if it doesn't exist
SELECT 'CREATE DATABASE astro_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'astro_db')\gexec

-- Connect to astro_db and create schema
\c astro_db

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create astro_profiles table
CREATE TABLE IF NOT EXISTS astro_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Link to Mastodon user (nullable for anonymous profiles)
    mastodon_user_id BIGINT UNIQUE,

    -- Profile name (for display)
    profile_name VARCHAR(255) NOT NULL,

    -- Birth data
    birth_date DATE NOT NULL,
    birth_time TIME NOT NULL,
    birth_timezone VARCHAR(64) NOT NULL DEFAULT 'UTC',

    -- Birth location
    birth_location JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Example: {"city": "Санкт-Петербург", "lat": 59.9343, "lon": 30.3351, "country": "Russia"}

    -- Calculated chart data (cached)
    chart_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Example: {
    --   "d1": {"ascendant": "Leo", "sun": {"sign": "Taurus", "house": 10}, ...},
    --   "d9": {...},
    --   "planets": [...]
    -- }

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Ayanamsa used for calculation
    ayanamsa VARCHAR(32) DEFAULT 'lahiri'
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_astro_profiles_mastodon_user_id
    ON astro_profiles(mastodon_user_id)
    WHERE mastodon_user_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_astro_profiles_created_at
    ON astro_profiles(created_at DESC);

-- GIN index for JSONB search (sun sign, moon sign queries)
CREATE INDEX IF NOT EXISTS idx_astro_profiles_chart_data
    ON astro_profiles USING GIN (chart_data jsonb_path_ops);

-- Function to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for updated_at
DROP TRIGGER IF EXISTS update_astro_profiles_updated_at ON astro_profiles;
CREATE TRIGGER update_astro_profiles_updated_at
    BEFORE UPDATE ON astro_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions to postgres user (already superuser, but explicit)
GRANT ALL PRIVILEGES ON DATABASE astro_db TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Verify creation
\echo '=== StarMeet Astro DB Initialized ==='
\dt astro_profiles
\echo '======================================'
