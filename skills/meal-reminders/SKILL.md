---
name: meal-reminders
description: "Proactively remind users to log meals at breakfast (10am), lunch (1pm), dinner (7pm) if not yet logged."
version: 1.0.0
author: Metabolix Agent
metadata:
  hermes:
    tags: [metabolix, reminders, proactive, meal-timing]
    related_skills: [meal-logging, metabolix-profile]
---

# Meal Reminders

Proactively check if meals are logged and remind users to eat and track.

## Timing Logic

Check at these times daily:
- **10:00 AM**: Breakfast check
- **1:00 PM**: Lunch check  
- **7:00 PM**: Dinner check

## Reminder Flow

```sh
# Check if meal type logged today
python3 "$HERMES_HOME/skills/meal-reminders/scripts/check_meals.py" --meal-type breakfast

# Returns: logged | not_logged
```

If **not_logged**, send proactive reminder via Plow Chat:
```
Haven't seen breakfast yet. Have you eaten?
Send a photo to log your macros and stay on track with your [goal] goal.
```

Personalize based on user's goal (lose_weight, gain_muscle, etc).
