<h1 align="center">Metabolix</h1>

<p align="center">
  <b>An autonomous fitness agent with a phone number that tracks your nutrition —<br>
  just send a photo of your meal.</b>
</p>

<p align="center">
  <a href="#install-5-minutes">Install</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#what-makes-it-different">What makes it different</a>
</p>

---

You finish eating and walk away. By the time you look at your phone, your macros
are logged and your dashboard is updated.

Send a food photo via text. Metabolix analyzes it **using AI vision**, calculates
every macro (calories, protein, carbs, fat), logs it to **your Google Sheet** via
Gemini, and texts you back with what's left in your budget. No app. No manual
entry. No spreadsheet work.

When your protein target is missed for 3 days straight, it stages high-protein
groceries in your Amazon cart, navigates to checkout, and **asks for approval**
before touching payment. One text: `CONFIRM BUY`. That's it.

<p align="center">
  <img src="docs/img/sms-confirmation.jpg" width="60%" alt="SMS confirmation showing macros logged and remaining budget">
  <br><i>What you get after every meal — macros logged, budget remaining, metabolic insight.</i>
</p>

## What makes it different

Every nutrition tracker is manual: you type the food, guess the portion, submit
the form. Metabolix is **vision-first and autonomous**:

- **Photo → logged** in 10 seconds. No typing, no searching databases.
- **TDEE-based targets** calculated scientifically (Mifflin-St Jeor BMR × activity).
- **Gemini-powered dashboards** — beautiful charts auto-generated, no manual formatting.
- **Proactive intervention** — detects protein deficits, stages groceries, awaits approval.
- **Monthly rollover** — new sheet auto-created, previous month's report emailed.

<p align="center">
  <img src="docs/img/dashboard.jpg" width="80%" alt="Google Sheets dashboard with calorie line chart, macro pie chart, and summary cards">
  <br><i>The dashboard Gemini creates: charts, cards, formatting — all automatic.</i>
</p>

## How it works

The agent **thinks** in a container; the work **happens** on your Mac via
[Plow Latch](https://plow.co/latch), and data lives in **your Google Sheet**.

```
  your phone ──iMessage──▶  Plow line ──▶  Hermes agent (Docker)
                                              │
                              ┌───────────────┼────────────────┐
                              ▼               ▼                ▼
                        Vision Analysis   Latch (approved)  Google Sheets
                        food → macros     open sheet ·      via Gemini:
                                          enable Gemini ·   create dashboard ·
                                          append data       log meals ·
                                                           update charts
```

Two inputs, one engine:

| | **Photo** | **Manual** |
|---|---|---|
| input | send food photo | text meal details |
| analysis | AI vision → portion + ingredients | parse text |
| calculation | calories, protein, carbs, fat | same |
| logging | **Gemini appends to sheet** + updates charts | same |
| verification | dashboard screenshot sent back | same |

## What a meal becomes

1. **Analyzed** — portions identified, ingredients recognized via vision.
2. **Calculated** — macros computed: calories (kcal), protein (g), carbs (g), fat (g).
3. **Logged via Gemini** — sheet opens, Gemini appends row, charts auto-update.
4. **Verified** — dashboard screenshot confirms entry.
5. **Texted back** — "🔥 450 kcal | 🍗 42g Pro | 🍞 28g Carb | 🥑 16g Fat — Remaining: 1250 kcal | 58g Protein needed."
6. **Remembered** — stored in SQLite + Google Sheet for weekly/monthly analysis.

<p align="center">
  <img src="docs/img/vision-analysis.jpg" width="50%" alt="Food photo being analyzed with overlays showing identified items">
  <br><i>Vision analysis: portions estimated, ingredients identified, macros calculated.</i>
</p>

## The TDEE science

Metabolix calculates your **Total Daily Energy Expenditure** using the Mifflin-St Jeor equation:

```
BMR (Male)   = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) + 5
BMR (Female) = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) - 161

TDEE = BMR × Activity Multiplier

Activity Levels:
- Sedentary: 1.2
- Lightly Active: 1.375
- Moderately Active: 1.55
- Very Active: 1.725
- Extra Active: 1.9
```

### Goal-based macro targets

| Goal | Calories | Protein | Fat | Carbs |
|------|----------|---------|-----|-------|
| **Maintain** | TDEE | 2.0g/kg | 25% | Remainder |
| **Lose Weight** | TDEE - 500 | 2.2g/kg | 25% | Remainder |
| **Gain Muscle** | TDEE + 300 | 2.4g/kg | 25% | Remainder |
| **Recomp** | TDEE | 2.5g/kg | 22% | Remainder |

## Grocery automation

When protein is missed 3+ days straight:

1. **Detects deficit** — tracks daily compliance vs. target.
2. **Opens Amazon Fresh** — via Latch, navigates to your cart.
3. **Stages high-protein items**:
   - 2× Greek Yogurt (Fage 0%, 500g) — $6.98 each
   - 1× Whey Protein Isolate (2lb) — $39.99
4. **Navigates to checkout** — stops at review page.
5. **Texts approval request**:
   ```
   ⚠️ Protein deficit detected (3 days < target).
   
   Staged in Amazon cart:
   - 2x Fage Greek Yogurt 0% (500g) - $6.98 each
   - 1x Optimum Whey Isolate (2lb) - $39.99
   
   Total: $53.95 (before tax)
   
   Reply 'CONFIRM BUY' to complete purchase.
   ```
6. **Waits for exact phrase** — `CONFIRM BUY`.
7. **Only then** clicks "Place Order".
8. **Sends receipt** — screenshot of order confirmation.

**It will NEVER execute payment without your explicit approval.**

## Monthly rollover

On the 1st of each month:

1. **Creates new sheet** — `[YourName]-[NewMonth]-Metabolix`.
2. **Uses Gemini** — sends same dashboard creation prompt, recreates structure in 30 seconds.
3. **Generates report** from previous month:
   - Total meals logged
   - Average daily: calories, protein, carbs, fat
   - Days on target vs. deficit
   - Weekly trends
   - Recommendations
4. **Emails report** — formatted professionally, sent to your configured email.
5. **Continues** — starts logging to new month's sheet.

<p align="center">
  <img src="docs/img/monthly-report.jpg" width="70%" alt="Monthly email report with stats and charts">
  <br><i>Monthly report: auto-generated, emailed on the 1st — no manual export.</i>
</p>

## Install (5 minutes)

### Before you start (2 minutes, once per machine)

You need **Docker**, **git**, **Python 3**, and a **Plow account**. Then:

```sh
git clone https://github.com/plow-pbc/plow-agents.git
export PATH="$PWD/plow-agents/bin:$PATH"
plow-agents login     # authenticates by texting you a code
```

If you have already done this for another agent, skip it.

### 1. Get the agent a phone line

```sh
plow-agents lines            # pick a free ln_... id
plow-agents mint ln_xxxxx    # writes ./plow-credentials
```

### 2. Clone and start

```sh
git clone https://github.com/yourusername/metabolix.git
cd metabolix
mv ../plow-credentials .     # or run `mint` from inside this directory
docker compose up --build -d
```

The first build pulls the Plow base image and takes a few minutes. After that:

```sh
docker compose logs -f agent   # wait for the gateway to come up
```

### 3. Text it

Text the number `plow-agents lines` showed you. Say `hey metabolix` or `set up my profile`. It walks you through:

- Name, age, gender
- Weight (kg), height (cm)
- Activity level (sedentary → extra active)
- Fitness goal (maintain, lose weight, gain muscle, recomp)
- Email for monthly reports

### 4. First meal

Send a photo of your food with `lunch` or `dinner`. Within 10 seconds:
- Macros calculated
- Google Sheet updated via Gemini
- Dashboard charts refreshed
- Confirmation texted back

**Nothing is configured by editing files.** Everything happens in the chat.

### Stopping

```sh
docker compose down       # keeps memory and data
docker compose down -v    # forgets everything, starts fresh
plow-agents revoke        # releases the phone line
```

## When it doesn't work

**`no such file or directory: ./plow-credentials`** — you ran `docker compose up`
before `plow-agents mint`. Compose created a *directory* at that path. Remove it,
run `mint`, then `up` again:

```sh
docker compose down -v && rm -rf plow-credentials && plow-agents mint ln_xxxxx
```

**The build fails pulling the base image** — `docker logout public.ecr.aws`. A
stale credential in Docker's config makes an anonymous public pull fail.

**It never texts you** — check `docker compose logs agent` for
`plow_chat connected`. If the credential file is wrong the container blocks on
purpose rather than starting half-configured.

**Gemini not working in Sheets** — ensure Google Workspace account with Gemini
enabled. If unavailable, Metabolix falls back to manual logging (slower but
functional).

## Commands

Check the agent's status:

```sh
# View profile and targets
docker compose exec --user hermes agent \
  python3 /var/lib/hermes/skills/metabolix-profile/scripts/profile.py show

# Today's summary
docker compose exec --user hermes agent \
  python3 /var/lib/hermes/skills/meal-logging/scripts/log_meal.py summary-today

# Monthly stats
docker compose exec --user hermes agent \
  python3 /var/lib/hermes/skills/meal-logging/scripts/log_meal.py monthly-stats --month 2026-09
```

## What it will not do

- Log anything without analyzing it first (no blind guesses).
- Execute grocery payments without explicit `CONFIRM BUY` approval.
- Upload food photos anywhere — analysis is local, vision API only.
- Share your data — everything stays in your Google Sheet and local SQLite.
- Make dietary recommendations — it tracks macros, you make nutrition decisions.

## The Plow tools it uses

- **[Latch](https://plow.co/latch)** — approved, sandboxed access to your Mac (Google Sheets, Amazon).
- **[hermes-plow-plugin](https://github.com/plow-pbc/hermes-plow-plugin)** — the agent's phone line.
- **Gemini in Google Sheets** — dashboard creation, data entry, chart updates.

## Under the hood

| Path | What |
|---|---|
| `runtime/persona.md` | Metabolix identity, core instructions, Gemini-first workflow |
| `skills/metabolix-profile/` | User profile, TDEE calculation, macro targets, sheet config |
| `skills/metabolix-profile/scripts/profile.py` | BMR/TDEE math, target calculation, CLI (284 lines) |
| `skills/meal-logging/` | Vision analysis, Gemini logging, verification, summaries |
| `skills/meal-logging/scripts/log_meal.py` | Meal database, verification tracking, stats (254 lines) |
| `skills/grocery-staging/` | Deficit detection, Amazon automation, approval gate |
| `compose.yml`, `Dockerfile` | Docker setup, Plow base image extension |

## Privacy & data

- **Local storage**: SQLite at `$HERMES_HOME/metabolix/metabolix.db` (inside Docker volume).
- **Your Google Sheet**: You own it, you control sharing.
- **No uploads**: Food photos analyzed locally, never uploaded.
- **No tracking**: No third-party analytics, no data sold.
- **Credentials**: Amazon, Google OAuth stored in Latch vault, never in chat.

## The Agent Index

This image ships the AI Worth Using usage reporter as a supervised service. It
reports token counts hourly — **no prompts, no message text, no file paths**.
The `AGENT_ID` in `compose.yml` is what it reports under.

## License

MIT — see [LICENSE](LICENSE).

Built on the Plow Hermes base image (Apache-2.0, © 2026 The Plow Collective) and
Nous Research's Hermes Agent. Not affiliated with either; "Plow" and "Hermes"
are their marks and this license grants no rights to them.

---

<p align="center">
  <b>Text a photo. Get your macros. Stay on track.</b>
</p>
