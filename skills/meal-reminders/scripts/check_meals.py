#!/usr/bin/env python3
"""Check if meal types have been logged today."""

import argparse
import os
import sqlite3
import sys
from datetime import date
from pathlib import Path


def database_path() -> Path:
    configured = os.environ.get("METABOLIX_PROFILE_DB")
    if configured:
        return Path(configured).expanduser()
    home = Path(os.environ.get("HERMES_HOME", "/var/lib/hermes"))
    return home / "metabolix" / "metabolix.db"


def check_meal_logged(meal_type: str) -> bool:
    """Check if meal_type has been logged today."""
    db_path = database_path()
    if not db_path.exists():
        return False
    
    conn = sqlite3.connect(db_path)
    today = date.today().isoformat()
    
    result = conn.execute("""
        SELECT COUNT(*) FROM meal_log
        WHERE date(timestamp) = ? AND meal_type = ?
    """, (today, meal_type)).fetchone()
    
    conn.close()
    return result[0] > 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--meal-type", required=True, choices=["breakfast", "lunch", "dinner"])
    args = parser.parse_args()
    
    if check_meal_logged(args.meal_type):
        print("logged")
    else:
        print("not_logged")


if __name__ == "__main__":
    main()
