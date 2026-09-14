# Metabolix Agent - Quick Start

## What is Metabolix?

Metabolix is an autonomous fitness and nutrition tracking agent that:
- 📸 Analyzes food photos using AI vision
- 📊 Logs meals to Google Sheets via Gemini (auto-creates dashboards)
- 💪 Calculates personalized macro targets (TDEE-based, scientifically accurate)
- 📱 Sends SMS confirmations via Plow Chat
- 🛒 Stages grocery orders when protein targets are missed
- 📧 Emails monthly nutrition reports

## Setup (5 minutes)

### Prerequisites

- Docker installed
- Git installed
- Python 3 installed
- Plow account ([sign up](https://plow.co))

### 1. Install Plow Agents CLI

```bash
git clone https://github.com/plow-pbc/plow-agents.git
export PATH="$PWD/plow-agents/bin:$PATH"
plow-agents login
```

### 2. Get a Phone Line

```bash
plow-agents lines            # Shows available lines
plow-agents mint ln_xxxxx    # Mints credentials
```

### 3. Build & Start Metabolix

```bash
git clone https://github.com/yourusername/metabolix.git
cd metabolix
mv ../plow-credentials .
docker compose up --build -d
```

### 4. First Message

Text your Plow line number. Say:
```
Hey Metabolix, set up my profile
```

Metabolix will ask for:
- **Name**: John
- **Age**: 30
- **Gender**: male
- **Weight**: 75 kg
- **Height**: 180 cm
- **Activity**: moderately_active
- **Goal**: lose_weight
- **Email**: john@example.com

### 5. Automatic Sheet Creation

Metabolix will:
1. Open `https://sheets.new` via Latch
2. Enable Gemini in Sheets
3. Send dashboard creation prompt to Gemini
4. Gemini creates "Log" sheet + "Dashboard" with charts
5. Save URL to configuration
6. Text you the link

**Result**: Beautiful dashboard ready in 30 seconds.

## Daily Usage

### Log a Meal (Primary: Photo)

Take a photo of your food and send it via text with:
```
Lunch
```

**Metabolix will**:
1. Analyze the image (identify foods, estimate portions)
2. Calculate: Calories, Protein, Carbs, Fat
3. Open your Google Sheet
4. Click Gemini sidebar
5. Send: "Add to Log: Meal: [name], Calories: X, Protein: Xg, Carbs: Xg, Fat: Xg"
6. Gemini appends row + updates all charts automatically
7. Verify in Dashboard tab
8. Reply with:
   ```
   Grilled Chicken Salad Logged.
   🔥 450 kcal | 🍗 42g Pro | 🍞 28g Carb | 🥑 16g Fat
   
   Remaining Budget: 1250 kcal | 58g Protein needed.
   Insight: High protein, excellent thermic effect.
   ```

**Time**: ~10 seconds

### Log a Meal (Fallback: Text)

If you don't have a photo:
```
Grilled chicken breast 200g, rice 150g, broccoli 100g
```

Metabolix parses text, calculates macros, logs same way.

### Check Today's Summary

```
What did I eat today?
```

**Returns**:
- All meals logged
- Total macros consumed
- Remaining budget vs. target
- Pacing insight

### Monthly Report

Automatic on 1st of month:
1. Generates stats from previous month
2. Creates new sheet for new month (via Gemini)
3. Emails report to your configured address

## Grocery Automation

**Trigger**: Protein target missed 3+ consecutive days

**What happens**:
1. Metabolix opens Amazon Fresh via Latch
2. Searches for high-protein items
3. Adds to cart: Greek Yogurt, Whey Protein
4. Navigates to checkout review page
5. Texts approval request:
   ```
   ⚠️ Protein deficit detected.
   
   Staged in cart:
   - 2x Greek Yogurt ($6.98 each)
   - 1x Whey Isolate ($39.99)
   
   Total: $53.95
   
   Reply 'CONFIRM BUY' to complete purchase.
   ```
6. **Waits** for exact phrase `CONFIRM BUY`
7. Only then clicks "Place Order"
8. Sends receipt screenshot

**Safety**: NEVER executes payment without explicit approval.

## Understanding Your Targets

Metabolix calculates scientifically:

### TDEE (Total Daily Energy Expenditure)
```
BMR = Mifflin-St Jeor equation based on age, gender, weight, height
TDEE = BMR × Activity Multiplier

Example:
- Male, 30yo, 75kg, 180cm
- Moderately active (1.55 multiplier)
- BMR: ~1,750 kcal
- TDEE: ~2,712 kcal
```

### Goal-Based Macros

**Lose Weight** (your example):
- Calories: 2,212 (TDEE - 500)
- Protein: 165g (2.2g/kg)
- Fat: 61g (25% of calories)
- Carbs: 330g (remainder)

**Why these numbers?**
- 500 cal deficit → ~0.5kg/week fat loss
- High protein preserves muscle
- 25% fat for hormonal health
- Carbs for energy and recovery

## Commands Reference

```bash
# View profile and targets
docker compose exec --user hermes agent \
  python3 /var/lib/hermes/skills/metabolix-profile/scripts/profile.py show

# Today's summary
docker compose exec --user hermes agent \
  python3 /var/lib/hermes/skills/meal-logging/scripts/log_meal.py summary-today

# Monthly stats
docker compose exec --user hermes agent \
  python3 /var/lib/hermes/skills/meal-logging/scripts/log_meal.py monthly-stats --month 2026-09

# View logs
docker compose logs -f agent
```

## Troubleshooting

### Sheet not logging?

**Check Gemini is enabled**:
1. Open your Google Sheet
2. Look for sparkle ✨ icon (top-right or sidebar)
3. If not visible: Extensions menu → Gemini

**Check Latch permissions**:
```bash
docker compose logs agent | grep -i latch
```

### Wrong macros calculated?

**Provide more context in photo message**:
```
Grilled chicken breast, 200g, with 100g rice and salad
```

Vision analysis improves with hints about portion sizes.

### Grocery staging not working?

**Check Amazon Fresh account**:
- Ensure logged into Amazon via Latch
- Verify Amazon Fresh available in your area
- Check Latch vault has Amazon credentials

### Gemini not responding in Sheets?

**Fallback mode activated**:
- Metabolix will use manual cell navigation
- Slower but functional
- Charts may not auto-update
- Report issue: Gemini may need Google Workspace account

## Privacy & Data

- **All data stored locally**: SQLite in Docker volume `/var/lib/hermes/metabolix/metabolix.db`
- **Google Sheets**: You own and control, can share/revoke anytime
- **No third-party tracking**: No analytics, no data sold
- **Food photos**: Analyzed locally, never uploaded or stored
- **Amazon credentials**: Stored in Latch vault, never in chat or logs

## Monthly Workflow Summary

**Days 1-30**: 
- Send food photos → Auto-logged in sheet
- Dashboard updates in real-time
- SMS confirmations after each meal

**Day 31 (Month End)**:
- Metabolix generates report from previous month
- Emails report to you
- Creates new sheet for new month (via Gemini, 30 seconds)
- Starts fresh tracking

**Result**: Each month preserved with historical data, clean slate for new month.

## What Happens Behind the Scenes

1. **You send photo** → Plow Chat receives
2. **Vision API analyzes** → Identifies foods, portions
3. **Python script calculates** → Macros based on nutrition database
4. **Logged to SQLite** → Local backup
5. **Latch opens sheet** → Your Google Sheet via browser automation
6. **Gemini activated** → Sidebar opened automatically
7. **Data sent to Gemini** → Natural language: "Add to Log: ..."
8. **Gemini appends** → New row + timestamp
9. **Charts auto-update** → Formulas refresh
10. **Screenshot taken** → Dashboard showing new data
11. **SMS sent** → Confirmation with screenshot

**No manual work**. Everything automated.

## Need Help?

### Check agent status
```bash
docker compose ps
```

### View real-time logs
```bash
docker compose logs -f agent
```

### Verify installation
```bash
# Should output: 1
docker compose exec agent grep -c 'You are Metabolix' /var/lib/hermes/SOUL.md

# Should show: grocery-staging, meal-logging, metabolix-profile
docker compose exec agent ls /var/lib/hermes/skills
```

### Reset everything
```bash
docker compose down -v
rm -rf plow-credentials
# Start from step 2 (mint new line)
```

## Tips for Best Results

1. **Clear photos**: Good lighting, full view of plate
2. **Include context**: "Dinner: grilled salmon with vegetables"
3. **Be consistent**: Log every meal for accurate weekly trends
4. **Trust the science**: TDEE-based targets are evidence-backed
5. **Review weekly**: Check Dashboard tab, identify patterns

## What's Next?

After 1 week:
- Enough data for weekly trends
- Protein compliance patterns visible
- First potential grocery intervention

After 1 month:
- Full monthly report emailed
- New month sheet auto-created
- Historical comparison available

After 3 months:
- Long-term trends clear
- Goal progress measurable
- Macro targets refineable

---

**Ready to start?** Text your Plow line: `Hey Metabolix, set up my profile`
