"""
Database utilities for StarMeet Astro UI
Handles PostgreSQL connection, initialization, and CRUD operations
"""
import os
import json
import logging
from datetime import datetime, date, time
from typing import Optional, List, Dict, Any

import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration from environment
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mastodon-db'),
    'port': os.getenv('DB_PORT', '5432'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'mastodon_secure_password'),
    'dbname': os.getenv('DB_NAME', 'astro_db')
}

SYSTEM_DB = 'postgres'  # System DB for creating new databases


def get_system_connection():
    """Connect to system postgres database (for DB creation)"""
    config = DB_CONFIG.copy()
    config['dbname'] = SYSTEM_DB
    return psycopg2.connect(**config)


def get_connection():
    """Connect to astro_db database"""
    return psycopg2.connect(**DB_CONFIG)


def init_database() -> bool:
    """
    Initialize the database with 3-stage approach:
    Stage A: Create database if not exists
    Stage B: Create schema/tables
    Stage C: Migrate JSON data if table is empty

    Returns True if successful
    """
    try:
        # Stage A: Create database
        logger.info("Stage A: Checking/creating database...")
        _create_database_if_not_exists()

        # Stage B: Create schema
        logger.info("Stage B: Creating schema...")
        _create_schema()

        # Stage C: Migrate JSON data
        logger.info("Stage C: Migrating JSON data...")
        _migrate_json_data()

        logger.info("Database initialization complete!")
        return True

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


def _create_database_if_not_exists():
    """Stage A: Create astro_db if it doesn't exist"""
    conn = get_system_connection()
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    try:
        cur = conn.cursor()

        # Check if database exists
        cur.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_CONFIG['dbname'],)
        )
        exists = cur.fetchone()

        if not exists:
            logger.info(f"Creating database: {DB_CONFIG['dbname']}")
            cur.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(DB_CONFIG['dbname'])
                )
            )
            logger.info("Database created successfully")
        else:
            logger.info(f"Database {DB_CONFIG['dbname']} already exists")

    finally:
        conn.close()


def _create_schema():
    """Stage B: Create tables in astro_db"""
    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS astro_profiles (
                id SERIAL PRIMARY KEY,
                display_name VARCHAR(255) NOT NULL,
                gender VARCHAR(50),
                birth_date DATE,
                birth_time TIME,
                birth_place VARCHAR(255),
                latitude FLOAT,
                longitude FLOAT,
                timezone VARCHAR(50),
                chart_data JSONB,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS idx_astro_profiles_name
            ON astro_profiles(display_name);

            CREATE INDEX IF NOT EXISTS idx_astro_profiles_created
            ON astro_profiles(created_at);
        """)

        conn.commit()
        logger.info("Schema created successfully")

    finally:
        conn.close()


def _migrate_json_data():
    """Stage C: Migrate data from saved_profiles.json if table is empty"""
    conn = get_connection()

    try:
        cur = conn.cursor()

        # Check if table has data
        cur.execute("SELECT COUNT(*) FROM astro_profiles")
        count = cur.fetchone()[0]

        if count > 0:
            logger.info(f"Table already has {count} profiles, skipping migration")
            return

        # Try to load JSON file
        json_paths = [
            '/app/saved_profiles.json',
            'saved_profiles.json',
            '/app/saved_profiles_backup.json'
        ]

        profiles = {}
        for path in json_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    profiles = json.load(f)
                    logger.info(f"Loaded profiles from {path}")
                    break
            except FileNotFoundError:
                continue

        if not profiles:
            logger.info("No JSON profiles found to migrate")
            return

        # Migrate each profile
        migrated = 0
        for name, data in profiles.items():
            try:
                birth_date = None
                birth_time = None

                if data.get('date'):
                    birth_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
                if data.get('time'):
                    birth_time = datetime.strptime(data['time'], '%H:%M').time()

                cur.execute("""
                    INSERT INTO astro_profiles
                    (display_name, gender, birth_date, birth_time, birth_place, chart_data)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    data.get('name', name),
                    data.get('gender'),
                    birth_date,
                    birth_time,
                    data.get('location'),
                    json.dumps(data)
                ))
                migrated += 1

            except Exception as e:
                logger.error(f"Failed to migrate profile {name}: {e}")

        conn.commit()
        logger.info(f"Migrated {migrated} profiles from JSON to PostgreSQL")

    finally:
        conn.close()


# CRUD Operations

def save_profile(
    display_name: str,
    gender: str,
    birth_date: date,
    birth_time: time,
    birth_place: str,
    latitude: float = None,
    longitude: float = None,
    timezone: str = None,
    chart_data: dict = None
) -> int:
    """
    Save a new profile or update existing one.
    Returns the profile ID.
    """
    conn = get_connection()

    try:
        cur = conn.cursor()

        # Check if profile exists
        cur.execute(
            "SELECT id FROM astro_profiles WHERE display_name = %s",
            (display_name,)
        )
        existing = cur.fetchone()

        if existing:
            # Update existing profile
            cur.execute("""
                UPDATE astro_profiles SET
                    gender = %s,
                    birth_date = %s,
                    birth_time = %s,
                    birth_place = %s,
                    latitude = %s,
                    longitude = %s,
                    timezone = %s,
                    chart_data = %s,
                    updated_at = NOW()
                WHERE display_name = %s
                RETURNING id
            """, (
                gender, birth_date, birth_time, birth_place,
                latitude, longitude, timezone,
                json.dumps(chart_data) if chart_data else None,
                display_name
            ))
            profile_id = cur.fetchone()[0]
            logger.info(f"Updated profile: {display_name} (ID: {profile_id})")
        else:
            # Insert new profile
            cur.execute("""
                INSERT INTO astro_profiles
                (display_name, gender, birth_date, birth_time, birth_place,
                 latitude, longitude, timezone, chart_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                display_name, gender, birth_date, birth_time, birth_place,
                latitude, longitude, timezone,
                json.dumps(chart_data) if chart_data else None
            ))
            profile_id = cur.fetchone()[0]
            logger.info(f"Created profile: {display_name} (ID: {profile_id})")

        conn.commit()
        return profile_id

    finally:
        conn.close()


def get_all_profiles() -> List[Dict[str, Any]]:
    """Get all profile names for sidebar list"""
    conn = get_connection()

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id, display_name, gender, birth_date, birth_time, birth_place
            FROM astro_profiles
            ORDER BY created_at DESC
        """)
        return cur.fetchall()

    finally:
        conn.close()


def get_profile_by_name(display_name: str) -> Optional[Dict[str, Any]]:
    """Get full profile by display name"""
    conn = get_connection()

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT * FROM astro_profiles WHERE display_name = %s
        """, (display_name,))
        return cur.fetchone()

    finally:
        conn.close()


def delete_profile(display_name: str) -> bool:
    """Delete a profile by name"""
    conn = get_connection()

    try:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM astro_profiles WHERE display_name = %s",
            (display_name,)
        )
        conn.commit()
        deleted = cur.rowcount > 0
        if deleted:
            logger.info(f"Deleted profile: {display_name}")
        return deleted

    finally:
        conn.close()


def test_connection() -> bool:
    """Test database connection"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False
