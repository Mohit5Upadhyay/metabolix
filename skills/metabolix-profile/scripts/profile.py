#!/usr/bin/env python3
"""Metabolix user profile, TDEE, targets, and sheet configuration."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "lightly_active": 1.375,
    "moderately_active": 1.55,
    "very_active": 1.725,
    "extra_active": 1.9,
}

GOALS = ("maintain", "lose_weight", "gain_muscle", "recomp")
SCHEMA_VERSION = 1


def database_path() -> Path:
    configured = os.environ.get("METABOLIX_PROFILE_DB")
    if configured:
        return Path(configured).expanduser()
    home = Path(os.environ.get("HERMES_HOME", "/var/lib/hermes"))
    return home / "metabolix" / "metabolix.db"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init_db(conn: sqlite3.Connection) -> None:
    """Initialize database schema."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL CHECK (gender IN ('male', 'female')),
            weight_kg REAL NOT NULL,
            height_cm REAL NOT NULL,
            activity_level TEXT NOT NULL,
            goal TEXT NOT NULL,
            email TEXT,
            grocery_service TEXT DEFAULT 'amazon_fresh',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sheet_config (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            sheet_url TEXT NOT NULL,
            current_month TEXT NOT NULL,
            sheet_name TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        INSERT OR IGNORE INTO schema_version (version) VALUES (?)
    """, (SCHEMA_VERSION,))
    conn.commit()


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor equation."""
    if gender == "male":
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:  # female
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """Calculate Total Daily Energy Expenditure."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    return bmr * multiplier


def calculate_targets(tdee: float, weight_kg: float, goal: str) -> dict:
    """Calculate macro targets based on goal."""
    if goal == "maintain":
        calories = tdee
        protein_g = 2.0 * weight_kg
        fat_pct = 0.25
    elif goal == "lose_weight":
        calories = tdee - 500
        protein_g = 2.2 * weight_kg
        fat_pct = 0.25
    elif goal == "gain_muscle":
        calories = tdee + 300
        protein_g = 2.4 * weight_kg
        fat_pct = 0.25
    else:  # recomp
        calories = tdee
        protein_g = 2.5 * weight_kg
        fat_pct = 0.22
    
    fat_g = (calories * fat_pct) / 9
    protein_calories = protein_g * 4
    fat_calories = fat_g * 9
    carbs_g = (calories - protein_calories - fat_calories) / 4
    
    return {
        "calories": round(calories),
        "protein_g": round(protein_g, 1),
        "carbs_g": round(carbs_g, 1),
        "fat_g": round(fat_g, 1),
    }


def cmd_init(args, conn: sqlite3.Connection) -> None:
    """Initialize user profile."""
    if args.activity not in ACTIVITY_MULTIPLIERS:
        print(f"Error: activity must be one of {list(ACTIVITY_MULTIPLIERS.keys())}", file=sys.stderr)
        sys.exit(1)
    if args.goal not in GOALS:
        print(f"Error: goal must be one of {GOALS}", file=sys.stderr)
        sys.exit(1)
    
    timestamp = now()
    conn.execute("""
        INSERT OR REPLACE INTO profile
        (id, name, age, gender, weight_kg, height_cm, activity_level, goal, email, created_at, updated_at)
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (args.name, args.age, args.gender, args.weight, args.height,
          args.activity, args.goal, args.email, timestamp, timestamp))
    conn.commit()
    
    print(f"Profile initialized for {args.name}")
    cmd_show(args, conn)


def cmd_show(args, conn: sqlite3.Connection) -> None:
    """Show current profile and targets."""
    row = conn.execute("SELECT * FROM profile WHERE id = 1").fetchone()
    if not row:
        print("No profile configured. Run 'init' first.", file=sys.stderr)
        sys.exit(1)
    
    cols = [d[0] for d in conn.execute("SELECT * FROM profile LIMIT 0").description]
    profile = dict(zip(cols, row))
    
    bmr = calculate_bmr(profile["weight_kg"], profile["height_cm"], profile["age"], profile["gender"])
    tdee = calculate_tdee(bmr, profile["activity_level"])
    targets = calculate_targets(tdee, profile["weight_kg"], profile["goal"])
    
    print(f"Profile: {profile['name']}, {profile['age']}yo {profile['gender']}")
    print(f"Stats: {profile['weight_kg']}kg, {profile['height_cm']}cm")
    print(f"Activity: {profile['activity_level']}")
    print(f"Goal: {profile['goal']}")
    print(f"Email: {profile['email']}")
    print(f"\nBMR: {round(bmr)} kcal")
    print(f"TDEE: {round(tdee)} kcal")
    print(f"\nDaily Targets:")
    print(f"  Calories: {targets['calories']} kcal")
    print(f"  Protein: {targets['protein_g']}g")
    print(f"  Carbs: {targets['carbs_g']}g")
    print(f"  Fat: {targets['fat_g']}g")


def cmd_targets(args, conn: sqlite3.Connection) -> None:
    """Output targets as JSON."""
    row = conn.execute("SELECT * FROM profile WHERE id = 1").fetchone()
    if not row:
        print("{}", file=sys.stderr)
        sys.exit(1)
    
    cols = [d[0] for d in conn.execute("SELECT * FROM profile LIMIT 0").description]
    profile = dict(zip(cols, row))
    
    bmr = calculate_bmr(profile["weight_kg"], profile["height_cm"], profile["age"], profile["gender"])
    tdee = calculate_tdee(bmr, profile["activity_level"])
    targets = calculate_targets(tdee, profile["weight_kg"], profile["goal"])
    
    print(json.dumps(targets))


def cmd_set_sheet(args, conn: sqlite3.Connection) -> None:
    """Set Google Sheet configuration."""
    conn.execute("""
        INSERT OR REPLACE INTO sheet_config
        (id, sheet_url, current_month, sheet_name, updated_at)
        VALUES (1, ?, ?, ?, ?)
    """, (args.url, args.month, args.name, now()))
    conn.commit()
    print(f"Sheet configured: {args.name} ({args.month})")


def cmd_get_sheet(args, conn: sqlite3.Connection) -> None:
    """Get current sheet configuration."""
    row = conn.execute("SELECT * FROM sheet_config WHERE id = 1").fetchone()
    if not row:
        print("{}", file=sys.stderr)
        sys.exit(1)
    
    cols = [d[0] for d in conn.execute("SELECT * FROM sheet_config LIMIT 0").description]
    config = dict(zip(cols, row))
    print(json.dumps({
        "sheet_url": config["sheet_url"],
        "current_month": config["current_month"],
        "sheet_name": config["sheet_name"],
    }))


def cmd_new_month(args, conn: sqlite3.Connection) -> None:
    """Signal that a new month sheet is needed."""
    current_month = datetime.now(timezone.utc).strftime("%Y-%m")
    row = conn.execute("SELECT current_month FROM sheet_config WHERE id = 1").fetchone()
    
    if row and row[0] == current_month:
        print(f"Already on current month: {current_month}")
    else:
        print(f"New month detected: {current_month}. Create new sheet.")
        sys.exit(2)  # Special exit code to signal new sheet needed


def cmd_reset(args, conn: sqlite3.Connection) -> None:
    """Reset all data - fresh start."""
    conn.execute("DELETE FROM profile")
    conn.execute("DELETE FROM sheet_config")
    conn.commit()
    print("Profile and sheet config reset. Ready for fresh setup.")


def main():
    parser = argparse.ArgumentParser(description="Metabolix profile management")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # init
    p_init = subparsers.add_parser("init", help="Initialize user profile")
    p_init.add_argument("--name", required=True)
    p_init.add_argument("--age", type=int, required=True)
    p_init.add_argument("--gender", required=True, choices=["male", "female"])
    p_init.add_argument("--weight", type=float, required=True, help="Weight in kg")
    p_init.add_argument("--height", type=float, required=True, help="Height in cm")
    p_init.add_argument("--activity", required=True, choices=list(ACTIVITY_MULTIPLIERS.keys()))
    p_init.add_argument("--goal", required=True, choices=GOALS)
    p_init.add_argument("--email", required=True)
    
    # show
    subparsers.add_parser("show", help="Show profile and targets")
    
    # targets
    subparsers.add_parser("targets", help="Output targets as JSON")
    
    # set-sheet
    p_sheet = subparsers.add_parser("set-sheet", help="Set Google Sheet config")
    p_sheet.add_argument("--url", required=True)
    p_sheet.add_argument("--month", required=True, help="Format: YYYY-MM")
    p_sheet.add_argument("--name", required=True, help="Sheet name")
    
    # get-sheet
    subparsers.add_parser("get-sheet", help="Get current sheet config as JSON")
    
    # new-month
    subparsers.add_parser("new-month", help="Check if new month sheet is needed")
    
    # reset
    subparsers.add_parser("reset", help="Reset all data for fresh start")
    
    args = parser.parse_args()
    
    db_path = database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    init_db(conn)
    
    commands = {
        "init": cmd_init,
        "show": cmd_show,
        "targets": cmd_targets,
        "set-sheet": cmd_set_sheet,
        "get-sheet": cmd_get_sheet,
        "new-month": cmd_new_month,
        "reset": cmd_reset,
    }
    
    commands[args.command](args, conn)
    conn.close()


if __name__ == "__main__":
    main()
