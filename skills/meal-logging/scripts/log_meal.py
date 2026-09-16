#!/usr/bin/env python3
"""Meal logging, verification, and daily summary."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone, date
from pathlib import Path


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
    """Initialize meal log schema with ALL analysis parameters."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS meal_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            meal_name TEXT NOT NULL,
            meal_type TEXT CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
            calories REAL NOT NULL,
            protein_g REAL NOT NULL,
            carbs_g REAL NOT NULL,
            fat_g REAL NOT NULL,
            glycemic_load REAL NOT NULL,
            thermic_effect TEXT NOT NULL,
            satiety_index REAL NOT NULL,
            verified BOOLEAN DEFAULT 0,
            sheet_row INTEGER
        )
    """)
    conn.commit()


def cmd_add(args, conn: sqlite3.Connection) -> None:
    """Add a meal to the log with ALL analysis parameters."""
    timestamp = now()
    meal_type = args.meal_type if hasattr(args, 'meal_type') else None
    
    cursor = conn.execute("""
        INSERT INTO meal_log
        (timestamp, meal_name, meal_type, calories, protein_g, carbs_g, fat_g, 
         glycemic_load, thermic_effect, satiety_index, verified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (timestamp, args.meal, meal_type, args.calories, args.protein, args.carbs, args.fat,
          args.glycemic_load, args.thermic_effect, args.satiety_index))
    
    meal_id = cursor.lastrowid
    conn.commit()
    
    print(json.dumps({
        "meal_id": meal_id,
        "timestamp": timestamp,
        "meal_name": args.meal,
        "meal_type": meal_type,
        "calories": args.calories,
        "protein_g": args.protein,
        "carbs_g": args.carbs,
        "fat_g": args.fat,
        "glycemic_load": args.glycemic_load,
        "thermic_effect": args.thermic_effect,
        "satiety_index": args.satiety_index,
        "status": "logged_locally",
    }))


def cmd_mark_verified(args, conn: sqlite3.Connection) -> None:
    """Mark a meal as verified in sheet."""
    conn.execute("""
        UPDATE meal_log
        SET verified = 1, sheet_row = ?
        WHERE id = ?
    """, (args.row, args.id))
    conn.commit()
    print(f"Meal {args.id} marked as verified (row {args.row})")


def cmd_summary_today(args, conn: sqlite3.Connection) -> None:
    """Get today's summary."""
    today = date.today().isoformat()
    
    rows = conn.execute("""
        SELECT meal_name, calories, protein_g, carbs_g, fat_g, verified
        FROM meal_log
        WHERE date(timestamp) = ?
        ORDER BY timestamp
    """, (today,)).fetchall()
    
    if not rows:
        print(json.dumps({
            "meals": [],
            "total_calories": 0,
            "total_protein_g": 0,
            "total_carbs_g": 0,
            "total_fat_g": 0,
            "meal_count": 0,
        }))
        return
    
    total_cal = sum(r[1] for r in rows)
    total_pro = sum(r[2] for r in rows)
    total_carb = sum(r[3] for r in rows)
    total_fat = sum(r[4] for r in rows)
    
    meals = [
        {
            "name": r[0],
            "calories": r[1],
            "protein_g": r[2],
            "carbs_g": r[3],
            "fat_g": r[4],
            "verified": bool(r[5]),
        }
        for r in rows
    ]
    
    print(json.dumps({
        "meals": meals,
        "total_calories": round(total_cal, 1),
        "total_protein_g": round(total_pro, 1),
        "total_carbs_g": round(total_carb, 1),
        "total_fat_g": round(total_fat, 1),
        "meal_count": len(rows),
    }))


def cmd_last_meal(args, conn: sqlite3.Connection) -> None:
    """Get the last logged meal."""
    row = conn.execute("""
        SELECT id, timestamp, meal_name, calories, protein_g, carbs_g, fat_g, insight, verified
        FROM meal_log
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()
    
    if not row:
        print("{}", file=sys.stderr)
        sys.exit(1)
    
    print(json.dumps({
        "meal_id": row[0],
        "timestamp": row[1],
        "meal_name": row[2],
        "calories": row[3],
        "protein_g": row[4],
        "carbs_g": row[5],
        "fat_g": row[6],
        "insight": row[7],
        "verified": bool(row[8]),
    }))


def cmd_reset(args, conn: sqlite3.Connection) -> None:
    """Reset all meal logs."""
    conn.execute("DELETE FROM meal_log")
    conn.commit()
    print("All meal logs deleted. Fresh start.")


def cmd_monthly_stats(args, conn: sqlite3.Connection) -> None:
    """Get monthly statistics."""
    rows = conn.execute("""
        SELECT 
            COUNT(*) as meal_count,
            AVG(calories) as avg_calories,
            AVG(protein_g) as avg_protein,
            AVG(carbs_g) as avg_carbs,
            AVG(fat_g) as avg_fat,
            SUM(calories) as total_calories,
            SUM(protein_g) as total_protein
        FROM meal_log
        WHERE strftime('%Y-%m', timestamp) = ?
    """, (args.month,)).fetchone()
    
    if not rows or rows[0] == 0:
        print(json.dumps({
            "meal_count": 0,
            "avg_daily_calories": 0,
            "avg_daily_protein_g": 0,
            "avg_daily_carbs_g": 0,
            "avg_daily_fat_g": 0,
        }))
        return
    
    # Count unique days
    days = conn.execute("""
        SELECT COUNT(DISTINCT date(timestamp))
        FROM meal_log
        WHERE strftime('%Y-%m', timestamp) = ?
    """, (args.month,)).fetchone()[0]
    
    print(json.dumps({
        "meal_count": rows[0],
        "days_tracked": days,
        "avg_daily_calories": round(rows[1], 1) if rows[1] else 0,
        "avg_daily_protein_g": round(rows[2], 1) if rows[2] else 0,
        "avg_daily_carbs_g": round(rows[3], 1) if rows[3] else 0,
        "avg_daily_fat_g": round(rows[4], 1) if rows[4] else 0,
        "total_calories": round(rows[5], 1) if rows[5] else 0,
        "total_protein_g": round(rows[6], 1) if rows[6] else 0,
    }))


def main():
    parser = argparse.ArgumentParser(description="Metabolix meal logging")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # add
    p_add = subparsers.add_parser("add", help="Log a meal")
    p_add.add_argument("--meal", required=True, help="Meal name")
    p_add.add_argument("--meal-type", dest="meal_type", choices=["breakfast", "lunch", "dinner", "snack"], help="Meal type")
    p_add.add_argument("--calories", type=float, required=True)
    p_add.add_argument("--protein", type=float, required=True, help="Protein in grams")
    p_add.add_argument("--carbs", type=float, required=True, help="Carbs in grams")
    p_add.add_argument("--fat", type=float, required=True, help="Fat in grams")
    p_add.add_argument("--glycemic-load", dest="glycemic_load", type=float, required=True, help="Glycemic load")
    p_add.add_argument("--thermic-effect", dest="thermic_effect", required=True, help="Thermic effect (low/moderate/high)")
    p_add.add_argument("--satiety-index", dest="satiety_index", type=float, required=True, help="Satiety index (0-5)")
    
    # mark-verified
    p_verify = subparsers.add_parser("mark-verified", help="Mark meal as verified in sheet")
    p_verify.add_argument("--id", type=int, required=True, help="Meal ID")
    p_verify.add_argument("--row", type=int, required=True, help="Sheet row number")
    
    # summary-today
    subparsers.add_parser("summary-today", help="Get today's summary as JSON")
    
    # last-meal
    subparsers.add_parser("last-meal", help="Get last logged meal as JSON")
    
    # monthly-stats
    p_monthly = subparsers.add_parser("monthly-stats", help="Get monthly statistics")
    p_monthly.add_argument("--month", required=True, help="Format: YYYY-MM")
    
    # reset
    subparsers.add_parser("reset", help="Delete all meal logs")
    
    args = parser.parse_args()
    
    db_path = database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    init_db(conn)
    
    commands = {
        "add": cmd_add,
        "mark-verified": cmd_mark_verified,
        "summary-today": cmd_summary_today,
        "last-meal": cmd_last_meal,
        "monthly-stats": cmd_monthly_stats,
        "reset": cmd_reset,
    }
    
    commands[args.command](args, conn)
    conn.close()


if __name__ == "__main__":
    main()
