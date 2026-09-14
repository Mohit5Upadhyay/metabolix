# Metabolix Agent - Architecture

## System Overview

Metabolix is built on the Plow Hermes agent framework, specialized for fitness and nutrition tracking with autonomous meal logging and proactive grocery intervention.

```
User (Plow Chat)
    ↓
Metabolix Agent (Docker Container)
    ↓
[Vision Analysis] → [Macro Calculation] → [Google Sheets Logging] → [SMS Confirmation]
                                              ↓
                                        [Deficit Detection]
                                              ↓
                                        [Grocery Staging]
```

## Core Components

### 1. Runtime Layer (`runtime/persona.md`)
- **Identity**: "You are Metabolix, an autonomous fitness, nutrition, and metabolic tracking agent"
- **Tone**: Concise, data-driven, actionable (no filler words)
- **Communication**: Exclusively via Plow Chat and Latch
- **Autonomy Rules**: What can/cannot be done without approval

### 2. Skills Layer (`skills/`)

#### metabolix-profile
**Purpose**: User profile, TDEE calculation, macro targets, sheet config

**Database Schema**:
```sql
profile (
  id, name, age, gender, weight_kg, height_cm,
  activity_level, goal, email, created_at, updated_at
)

sheet_config (
  id, sheet_url, current_month, sheet_name, updated_at
)
```

**Key Functions**:
- `calculate_bmr()`: Mifflin-St Jeor equation
- `calculate_tdee()`: BMR × activity multiplier
- `calculate_targets()`: Goal-based macro split

**Commands**:
- `init`: Initialize profile
- `show`: Display profile and targets
- `targets`: Output targets as JSON
- `set-sheet`: Configure Google Sheet
- `new-month`: Check if new sheet needed

#### meal-logging
**Purpose**: Food analysis, logging, verification, summaries

**Database Schema**:
```sql
meal_log (
  id, timestamp, meal_name, calories, protein_g,
  carbs_g, fat_g, insight, verified, sheet_row
)
```

**Workflow**:
1. User sends food photo via Plow Chat
2. Agent analyzes image (vision API)
3. Calculates macros
4. Logs to local DB: `add` command
5. Uses Latch to open Google Sheet
6. Appends row with meal data
7. Verifies entry visually
8. Marks as verified: `mark-verified` command
9. Sends SMS confirmation with screenshot

**Commands**:
- `add`: Log meal to local DB
- `mark-verified`: Mark as verified in sheet
- `summary-today`: Get today's totals
- `last-meal`: Get most recent meal
- `monthly-stats`: Aggregate monthly data

#### grocery-staging
**Purpose**: Detect deficits, stage groceries, approval gate

**Trigger Logic**:
- 3+ consecutive days < 85% protein target
- OR weekly average < 90% protein target

**Workflow**:
1. Check daily/weekly protein compliance
2. If deficit detected: Use Latch to open Amazon Fresh
3. Search and add high-protein items to cart
4. Navigate to checkout review (DO NOT proceed to payment)
5. Send approval request via Plow Chat
6. Wait for exact phrase: "CONFIRM BUY"
7. Only then: Click final payment button
8. Screenshot order confirmation
9. Send receipt via Plow Chat

**Critical Safety**:
- **FORBIDDEN**: Execute payment without "CONFIRM BUY"
- Any other response: Cancel, change, or wait
- No auto-purchase ever

### 3. Image Layer (`image/`)
Standard s6-overlay supervisor config for Agent Index reporting (hourly usage stats to AI Worth Using Agent Index).

### 4. Integration Layer

**Plow Chat**:
- All user communication
- SMS-style confirmations
- Approval requests
- Monthly reports

**Plow Latch**:
- Browser automation (Google Sheets, Amazon Fresh)
- Vault access (credentials)
- Mac environment control

**Google Sheets**:
- Monthly tracking sheets
- Format: `[UserName]-[MonthName]-Metabolix`
- Columns: Timestamp, Meal, Calories, Protein, Carbs, Fat, Insights

## Data Flow

### Meal Logging Flow
```
Photo → Vision Analysis → Macro Calculation
  ↓
Local DB Insert (meal_log)
  ↓
Latch: Open Google Sheet
  ↓
Append Row (Timestamp, Meal, Calories, Protein, Carbs, Fat, Insight)
  ↓
Visual Verification
  ↓
Update DB (verified=1, sheet_row=N)
  ↓
Plow Chat: Send confirmation + screenshot
```

### Monthly Rollover Flow
```
Day 1 of new month
  ↓
Check: current_month != actual month
  ↓
Latch: Create new Google Sheet ([Name]-[NewMonth]-Metabolix)
  ↓
Update sheet_config (sheet_url, current_month, sheet_name)
  ↓
Generate monthly report from meal_log
  ↓
Email report to user
  ↓
Continue logging to new sheet
```

### Grocery Staging Flow
```
Daily Protein Check
  ↓
IF deficit detected:
  ↓
Latch: Open Amazon Fresh
  ↓
Add items to cart
  ↓
Navigate to checkout review
  ↓
Plow Chat: "⚠️ Protein deficit. Staged items. Reply 'CONFIRM BUY'"
  ↓
Wait for user response
  ↓
IF "CONFIRM BUY":
  ↓
  Click "Place Order"
  ↓
  Screenshot confirmation
  ↓
  Plow Chat: Send receipt
ELSE:
  ↓
  Cancel or modify based on response
```

## TDEE & Macro Calculations

### BMR (Basal Metabolic Rate)
```python
# Mifflin-St Jeor Equation
Male:   BMR = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) + 5
Female: BMR = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) - 161
```

### TDEE (Total Daily Energy Expenditure)
```python
TDEE = BMR × Activity Multiplier

Activity Multipliers:
- sedentary: 1.2
- lightly_active: 1.375
- moderately_active: 1.55
- very_active: 1.725
- extra_active: 1.9
```

### Macro Targets by Goal

**Maintain Weight**:
- Calories: TDEE
- Protein: 2.0g/kg
- Fat: 25% of calories
- Carbs: Remainder

**Lose Weight**:
- Calories: TDEE - 500
- Protein: 2.2g/kg (preserve muscle)
- Fat: 25% of calories
- Carbs: Remainder

**Gain Muscle**:
- Calories: TDEE + 300
- Protein: 2.4g/kg
- Fat: 25% of calories
- Carbs: Remainder

**Recomp (Simultaneous fat loss + muscle gain)**:
- Calories: TDEE
- Protein: 2.5g/kg (highest)
- Fat: 22% of calories
- Carbs: Remainder

## Database Schema

### Single SQLite DB: `$HERMES_HOME/metabolix/metabolix.db`

```sql
-- User profile and settings
CREATE TABLE profile (
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
);

-- Google Sheet tracking
CREATE TABLE sheet_config (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    sheet_url TEXT NOT NULL,
    current_month TEXT NOT NULL,
    sheet_name TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Meal log (local mirror of Google Sheet)
CREATE TABLE meal_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    meal_name TEXT NOT NULL,
    calories REAL NOT NULL,
    protein_g REAL NOT NULL,
    carbs_g REAL NOT NULL,
    fat_g REAL NOT NULL,
    insight TEXT,
    verified BOOLEAN DEFAULT 0,
    sheet_row INTEGER
);
```

## Autonomy & Safety

### Autonomous (No approval required)
- Food photo analysis
- Macro calculation
- Local DB logging
- Google Sheets logging
- Visual verification
- SMS confirmations
- Deficit detection
- Grocery cart staging
- Monthly report generation

### Approval Required
- **Final payment execution**: Requires exact phrase "CONFIRM BUY"
- **Never allowed without approval**:
  - Money movement
  - Destructive operations
  - Credential changes

### Safety Gates
1. **Grocery Payment**: Hardcoded approval gate - cannot be bypassed
2. **Sheet Verification**: Must visually confirm logged row before marking verified
3. **Month Rollover**: Automatic but preserves all historical data
4. **Email Reports**: Only sent to user-configured email address

## Error Handling

### Sheet Logging Failures
- Retry once
- If fails again: Report error, mark meal as unverified
- User can manually add to sheet

### Verification Failures
- Alert user
- Keep meal in DB as unverified
- Continue tracking but note discrepancy

### Grocery Staging Failures
- Out of stock: Suggest alternatives, re-request approval
- Payment fails: Report error, do NOT retry
- Cart cleared: Re-stage and re-request approval

## Extension Points

### Adding New Skills
Follow pattern:
```
skills/new-skill/
  ├── SKILL.md (metadata + instructions)
  └── scripts/
      └── helper.py (Python tools)
```

### Adding New Data
Extend DB schema in relevant script's `init_db()` function.

### Adding New Integrations
Use Latch for browser/Mac automation. Follow approval patterns from grocery-staging.

## Deployment

### Build
```bash
docker compose build
```

### Run
```bash
docker compose up -d
```

### Credentials
Place Plow credentials in `./plow-credentials` (auto-mounted read-only).

### Persistence
Volume `agent-home` persists `/var/lib/hermes` across restarts:
- SQLite DB
- Skills
- Session state

## Monitoring

### Logs
```bash
docker compose logs -f agent
```

### Diagnostics
```bash
# Verify persona
docker compose exec agent grep -c 'You are Metabolix' /var/lib/hermes/SOUL.md

# List skills
docker compose exec agent ls /var/lib/hermes/skills

# Check DB
docker compose exec --user hermes agent \
  sqlite3 /var/lib/hermes/metabolix/metabolix.db "SELECT * FROM profile"
```

### Agent Index Reporting
Hourly reporting to AI Worth Using Agent Index (opt-in usage stats).

## Comparison: Traditional Nutrition Apps vs Metabolix

| Aspect | Traditional Apps | Metabolix |
|--------|------------------|-----------||
| Input Method | Manual typing, database search | Photo → AI vision analysis |
| Macro Calculation | User estimates or barcode scan | Automatic from vision + nutrition DB |
| Dashboard | Static or requires manual export | Gemini auto-creates, live updates |
| Intervention | None | Proactive grocery staging on deficits |
| Approval Required | N/A | Only for payment execution |
| Data Storage | Cloud-based proprietary | Your Google Sheet + local SQLite |
| Monthly Reports | Manual export or premium feature | Auto-generated + emailed |
| Speed per Meal | 1-2 minutes (typing, searching) | 10 seconds (photo → logged) |

Metabolix architectural pattern:
- Hermes runtime (Plow Hermes base image)
- Plow Chat communication (iMessage/SMS)
- Latch automation (Mac/browser control)
- Skill-based modular design
- SQLite persistence
- Docker containerization
- Gemini-first workflow
