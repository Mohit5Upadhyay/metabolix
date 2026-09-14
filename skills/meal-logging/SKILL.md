---
name: meal-logging
description: "Analyze food images, calculate macros, log via Gemini in Sheets, verify entries, and send SMS confirmations."
version: 1.0.0
author: Metabolix Agent
metadata:
  hermes:
    tags: [metabolix, meals, logging, macros, calories, nutrition, gemini]
    related_skills: [metabolix-profile]
---

# Meal Logging via Gemini

Analyze food photos, calculate nutritional data, log to Google Sheets using Gemini, and confirm via SMS.

## Vision Analysis Workflow

When user sends food photo:

1. **Analyze Image**: Identify food items, estimate portions using visual cues (hand size, plate size, common containers)

2. **Calculate Macros**: For each identified food:
   - Calories (kcal)
   - Protein (g)
   - Carbohydrates (g)
   - Fat (g)
   - Sum totals for the meal

3. **Assess Metabolic Impact**:
   - Thermic effect: High for protein, moderate for carbs, low for fat
   - Glycemic load: Estimate based on carb type and quantity
   - Satiety index: Predict fullness duration

## Gemini-Based Logging (PRIMARY METHOD)

**CRITICAL**: Use Gemini for ALL sheet operations. Do NOT manually navigate cells.

### Step 1: Log to Local Database
```sh
python3 "$HERMES_HOME/skills/meal-logging/scripts/log_meal.py" add \
  --meal "Grilled Chicken Salad" \
  --calories 450 --protein 42 --carbs 28 --fat 16 \
  --insight "High protein, low glycemic, excellent thermic effect"
```

Returns meal_id for verification later.

### Step 2: Open Sheet and Activate Gemini
1. Get sheet URL from profile:
   ```sh
   python3 "$HERMES_HOME/skills/metabolix-profile/scripts/profile.py" get-sheet
   ```
2. Use Latch browser to navigate to sheet URL
3. Click Gemini icon (sparkle ✨) in sidebar or top-right
4. If Gemini not visible:
   - Try "Help me organize" button
   - Or Extensions menu → Gemini
   - Wait 2-3 seconds for panel to load

### Step 3: Send Data to Gemini
Use this EXACT format:

```
Add to Log sheet:
Meal: Grilled Chicken Salad
Calories: 450
Protein: 42g
Carbs: 28g
Fat: 16g
Insight: High protein, low glycemic, excellent thermic effect
```

### Step 4: Let Gemini Work
Gemini will automatically:
- Add new row with current timestamp
- Input all data in correct columns
- Update Dashboard charts (calories line chart, macro pie chart)
- Apply conditional formatting (green/yellow/red based on targets)
- Recalculate summary cards

Wait 3-5 seconds for completion.

### Step 5: Verify Entry
1. Navigate to "Dashboard" tab
2. Check that:
   - Total Meals count increased
   - Avg Calories updated
   - Line chart has new data point
   - Pie chart reflects new macros
3. Note the row number from "Log" sheet

### Step 6: Mark as Verified
```sh
python3 "$HERMES_HOME/skills/meal-logging/scripts/log_meal.py" mark-verified \
  --id [meal_id_from_step1] --row [row_number_from_sheet]
```

### Step 7: Send SMS Confirmation
Format:
```
Grilled Chicken Salad Logged.
🔥 450 kcal | 🍗 42g Pro | 🍞 28g Carb | 🥑 16g Fat

Remaining Budget: 1250 kcal | 58g Protein needed.
Insight: High protein meal, excellent thermic effect. On track for daily target.
```

Attach screenshot of updated Dashboard tab showing new data point.

## Manual Fallback (ONLY IF GEMINI COMPLETELY FAILS)

If Gemini is unavailable after 2-3 attempts:

1. Navigate to "Log" sheet manually
2. Scroll to last row
3. Click next empty row
4. Manually enter: Timestamp | Meal | Calories | Protein | Carbs | Fat | Insight
5. Charts should auto-update via formulas
6. Verify and mark verified
7. Report to user: "Gemini unavailable, used manual logging"

## Daily Summary

```sh
# Get today's summary
python3 "$HERMES_HOME/skills/meal-logging/scripts/log_meal.py" summary-today
```

Returns:
- Total calories, protein, carbs, fat consumed
- Remaining budget vs. target
- Meals logged today
- Pacing insight (on track, ahead, behind)

Can also ask Gemini:
```
Summarize today's Log entries: total macros, meals count, and compliance vs targets
```

## Error Handling

- **Sheet URL not configured**: Trigger initialization
- **Month changed**: Create new sheet automatically via Gemini
- **Gemini not responding**: Wait 5 seconds, retry once, then use manual fallback
- **Verification fails**: Alert user, mark entry as unverified but keep in DB
- **Charts not updating**: Check if formulas are intact, ask Gemini to fix

## Why Gemini?

- **10x Faster**: No manual cell navigation
- **Auto-Updates**: Charts refresh automatically
- **Error-Free**: Gemini handles formatting and formulas
- **Beautiful**: Professional dashboard without manual design
- **Natural Language**: Simple commands, no complex automation
