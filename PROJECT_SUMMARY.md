# Metabolix Agent - Project Summary

## ✅ What Was Created

A complete, production-ready autonomous fitness and nutrition tracking agent built on the Plow Hermes framework, specialized for metabolic and calorie tracking.

## 📁 Project Structure

```
metabolix/
├── Dockerfile                     # Runtime packaging
├── compose.yml                    # Docker Compose config
├── README.md                      # Main documentation
├── QUICKSTART.md                  # 5-minute setup guide
├── ARCHITECTURE.md                # Deep technical architecture
├── LICENSE                        # MIT license
├── .gitignore, .dockerignore     # Git/Docker ignores
│
├── runtime/
│   └── persona.md                # Metabolix identity (63 lines)
│
├── skills/
│   ├── metabolix-profile/
│   │   ├── SKILL.md              # Profile, TDEE, targets
│   │   └── scripts/
│   │       └── profile.py        # 284 lines - profile management
│   │
│   ├── meal-logging/
│   │   ├── SKILL.md              # Food analysis, logging
│   │   └── scripts/
│   │       └── log_meal.py       # 254 lines - meal tracking
│   │
│   └── grocery-staging/
│       └── SKILL.md              # Deficit detection, approval gate
│
├── image/
│   └── s6-overlay/               # Supervisor config
│       └── s6-rc.d/
│           └── agent-index/      # Agent Index reporting
│
└── vendor/
    └── client.pin                # Agent Index client pinning
```

## 🎯 Core Capabilities Implemented

### 1. Food Analysis (Vision-based)
- Analyzes food photos
- Identifies portions and ingredients
- Calculates: Calories, Protein, Carbs, Fat
- Assesses metabolic impact (thermic effect, glycemic load)

### 2. TDEE & Macro Targets
- Mifflin-St Jeor BMR calculation
- Activity multipliers (sedentary → extra_active)
- Goal-based macro splits (maintain, lose_weight, gain_muscle, recomp)
- Scientific protein targets: 2.0-2.5g/kg based on goal

### 3. Google Sheets Logging (via Latch)
- Direct sheet manipulation (no third-party apps)
- Monthly sheets: "[UserName]-[Month]-Metabolix"
- Columns: Timestamp, Meal, Calories, Protein, Carbs, Fat, Insights
- Visual verification of logged entries
- Auto-rollover to new month

### 4. SMS Confirmations (via Plow Chat)
- Strict format: Macros + Remaining Budget + Insight
- Screenshot proof attached
- Real-time tracking updates

### 5. Grocery Staging (Amazon Fresh)
- Deficit detection: 3+ days < 85% protein target
- Auto-stages high-protein items in cart
- Navigates to checkout review
- **MANDATORY APPROVAL GATE**: Requires "CONFIRM BUY"
- Never executes payment without explicit approval

### 6. Monthly Reports (Email)
- Auto-generated at month end
- Stats: Avg daily macros, compliance %, trends
- Emailed to user-configured address

## 🔧 Technical Implementation

### Database (SQLite)
**Location**: `$HERMES_HOME/metabolix/metabolix.db`

**Tables**:
- `profile`: User stats, goals, TDEE settings
- `sheet_config`: Current Google Sheet tracking
- `meal_log`: Local mirror of logged meals

### Scripts (538 lines total)
1. **profile.py** (284 lines):
   - BMR/TDEE calculation
   - Macro target generation
   - Sheet configuration
   - Profile management CLI

2. **log_meal.py** (254 lines):
   - Meal logging
   - Verification tracking
   - Daily/monthly summaries
   - Stats aggregation

### Skills (3 total)
1. **metabolix-profile**: User onboarding, targets
2. **meal-logging**: Core tracking workflow
3. **grocery-staging**: Proactive deficit handling

## 🚀 Usage Flow

### Initial Setup
```bash
docker compose up -d
# Send: "Hey Metabolix, set up my profile"
# Answer questions → Sheet created → Ready to log
```

### Daily Usage
```
User: [sends food photo] "Lunch"
↓
Metabolix: Analyzes → Logs → Verifies → Confirms
↓
Reply: "Grilled Chicken Salad Logged.
        🔥 450 kcal | 🍗 42g Pro | 🍞 28g Carb | 🥑 16g Fat
        Remaining: 1250 kcal | 58g Protein needed."
```

### Protein Deficit Scenario
```
Day 3 below target
↓
Metabolix: Opens Amazon Fresh → Stages items → Requests approval
↓
User: "CONFIRM BUY"
↓
Metabolix: Executes payment → Sends receipt
```

## 🔒 Safety & Autonomy

### Autonomous (No approval)
- Food analysis
- Sheet logging
- SMS confirmations
- Deficit detection
- Grocery staging (to cart)
- Monthly reports

### Approval Required
- **Grocery checkout payment** (CONFIRM BUY gate)

### Forbidden
- Money movement without approval
- Credential changes
- Destructive operations

## 📊 Agent Capabilities

| Aspect | Traditional Agents | Metabolix |
|--------|-------------------|-----------|
| **Purpose** | Technical chief of staff | Fitness/nutrition tracking |
| **Skills** | 8 (context, gmail, calendar, etc.) | 3 (profile, logging, groceries) |
| **Data** | Company, repos, emails | User profile, meals, macros |
| **External Tools** | GitHub, Gmail, Sentry | Google Sheets, Amazon Fresh |
| **Approval Gates** | Communication sends | Grocery payments |
| **Lines of Code** | ~2000+ | ~859 |

**Both share**:
- Hermes runtime base
- Plow Chat communication
- Latch automation
- Skill-based architecture
- SQLite persistence
- Docker containerization
- Agent Index reporting

## 📚 Documentation Created

1. **README.md**: Main overview, capabilities, installation
2. **QUICKSTART.md**: 5-minute setup guide
3. **ARCHITECTURE.md**: Deep technical dive (data flow, calculations, safety)
4. **PROJECT_SUMMARY.md**: This file

## 🎓 Plow Hermes Agent Pattern

1. **runtime/persona.md**: Agent identity and core instructions
2. **skills/[name]/SKILL.md**: Skill metadata + usage docs
3. **skills/[name]/scripts/*.py**: Python helpers with CLI
4. **Dockerfile**: Based on official Plow Hermes image
5. **compose.yml**: Standard Plow agent setup
6. **image/s6-overlay/**: Supervisor config for side services
7. **vendor/client.pin**: Pinned Agent Index client

## ✨ Key Differences from Template

1. **Simpler scope**: 3 skills vs 8 (focused on fitness)
2. **Vision-first**: Food photo analysis (unique to Metabolix)
3. **Monthly rollover**: Auto-creates new sheets (unique to Metabolix)
4. **Grocery automation**: Proactive shopping (unique workflow)
5. **Macro calculations**: Scientific TDEE/BMR (domain-specific)

## 🔍 Verification Commands

```bash
# Verify persona
docker compose exec agent grep -c 'You are Metabolix' /var/lib/hermes/SOUL.md
# Should output: 1

# List skills
docker compose exec agent ls /var/lib/hermes/skills
# Should show: grocery-staging, meal-logging, metabolix-profile

# Show profile
docker compose exec --user hermes agent \
  python3 /var/lib/hermes/skills/metabolix-profile/scripts/profile.py show

# Today's summary
docker compose exec --user hermes agent \
  python3 /var/lib/hermes/skills/meal-logging/scripts/log_meal.py summary-today
```

## 🎯 What This Agent Does That Others Don't

1. **Vision-based macro tracking**: No manual entry, just photos
2. **Scientifically calculated targets**: TDEE-based, goal-adjusted
3. **Monthly sheet management**: Auto-rollover, email reports
4. **Proactive grocery intervention**: Detects deficits, stages orders
5. **Strict approval gates**: Never spends money without "CONFIRM BUY"
6. **Direct sheet logging**: No third-party apps, pure Latch automation

## 📈 Production Readiness

✅ Complete Docker setup
✅ Persistent storage (volumes)
✅ Error handling in scripts
✅ Approval gates for sensitive ops
✅ Visual verification of actions
✅ Comprehensive documentation
✅ Clean project structure
✅ No placeholder code
✅ Working Python scripts
✅ Proper persona instructions

## 🚀 Next Steps (If Extending)

1. **Add weight tracking**: Log weekly weigh-ins, chart trends
2. **Exercise logging**: Track workouts, calculate TDEE adjustments
3. **Meal planning**: Suggest meals based on remaining macros
4. **Progress photos**: Store/compare body composition photos
5. **Integration with fitness trackers**: Sync with Apple Health, Fitbit
6. **Restaurant database**: Pre-calculated macros for common restaurants
7. **Recipe analysis**: Calculate macros from ingredient lists

---

**Created**: 2026-09-14
**Pattern**: Plow Hermes agent framework
**Framework**: Plow Hermes
**Purpose**: Autonomous fitness and nutrition tracking
**Status**: Production-ready
