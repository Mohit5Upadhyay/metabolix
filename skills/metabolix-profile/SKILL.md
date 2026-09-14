---
name: metabolix-profile
description: "Store user profile, fitness goals, TDEE calculation, Google Sheets config, and nutritional targets."
version: 1.0.0
author: Metabolix Agent
metadata:
  hermes:
    tags: [metabolix, profile, fitness, nutrition, goals, tdee]
    related_skills: [meal-logging, grocery-staging]
---

# Metabolix Profile

Store and manage user fitness profile, nutritional targets, Google Sheets configuration, and monthly tracking state. All Metabolix state shares `$HERMES_HOME/metabolix/metabolix.db`.

## Initialization

On first run, collect:

1. Name, age, gender, weight (kg), height (cm)
2. Activity level (sedentary, lightly_active, moderately_active, very_active, extra_active)
3. Fitness goal (maintain, lose_weight, gain_muscle, recomp)
4. Email address for monthly reports
5. Preferred grocery service (amazon_fresh, instacart, etc.)

Calculate TDEE using Mifflin-St Jeor equation:
- Male BMR: (10 × weight_kg) + (6.25 × height_cm) - (5 × age) + 5
- Female BMR: (10 × weight_kg) + (6.25 × height_cm) - (5 × age) - 161
- TDEE = BMR × activity_multiplier

Activity multipliers:
- sedentary: 1.2
- lightly_active: 1.375
- moderately_active: 1.55
- very_active: 1.725
- extra_active: 1.9

## Target Macros

Calculate based on goal:
- **Maintain**: Calories = TDEE, Protein = 2.0g/kg, Fat = 25% calories, Carbs = remainder
- **Lose Weight**: Calories = TDEE - 500, Protein = 2.2g/kg, Fat = 25% calories, Carbs = remainder
- **Gain Muscle**: Calories = TDEE + 300, Protein = 2.4g/kg, Fat = 25% calories, Carbs = remainder
- **Recomp**: Calories = TDEE, Protein = 2.5g/kg, Fat = 22% calories, Carbs = remainder

## Google Sheets Config

Store current sheet URL, month, and sheet name. When month changes, create new sheet:

```sh
python3 "$HERMES_HOME/skills/metabolix-profile/scripts/profile.py" new-month
```

## Profile Commands

```sh
# Show current profile and targets
python3 "$HERMES_HOME/skills/metabolix-profile/scripts/profile.py" show

# Initialize user profile
python3 "$HERMES_HOME/skills/metabolix-profile/scripts/profile.py" init \
  --name "John" --age 30 --gender male --weight 75 --height 180 \
  --activity moderately_active --goal lose_weight --email "john@example.com"

# Update Google Sheet config
python3 "$HERMES_HOME/skills/metabolix-profile/scripts/profile.py" set-sheet \
  --url "https://docs.google.com/spreadsheets/d/..." --month "2026-09"

# Get current targets
python3 "$HERMES_HOME/skills/metabolix-profile/scripts/profile.py" targets
```

## Monthly Report

At end of month, generate report with:
- Total meals logged
- Average daily: calories, protein, carbs, fat
- Days on/off target
- Weight trend (if tracked)
- Insights and recommendations

Email report using stored email address.
