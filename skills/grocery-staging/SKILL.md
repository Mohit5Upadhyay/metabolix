---
name: grocery-staging
description: "Detect protein deficits and stage high-protein groceries with mandatory approval before checkout."
version: 1.0.0
author: Metabolix Agent
metadata:
  hermes:
    tags: [metabolix, groceries, protein, amazon, shopping]
    related_skills: [metabolix-profile, meal-logging]
---

# Grocery Staging

Proactively detect protein deficits and stage recommended high-protein items in user's grocery cart.

## Deficit Detection

Monitor weekly protein intake vs. target. If user is consistently falling short:

```sh
python3 "$HERMES_HOME/skills/meal-logging/scripts/log_meal.py" summary-today
python3 "$HERMES_HOME/skills/metabolix-profile/scripts/profile.py" targets
```

Trigger staging when:
- 3+ consecutive days below 85% protein target
- Weekly average < 90% protein target

## High-Protein Recommendations

Common items to stage:
- Greek Yogurt (Fage Total 0%, 500g): ~18g protein
- Whey Protein Isolate (Optimum Nutrition, 2lb): ~24g per scoop
- Chicken Breast (boneless, 1kg): ~30g per 100g
- Cottage Cheese (low-fat, 500g): ~12g per 100g
- Eggs (dozen): ~6g per egg

## Staging Workflow via Latch

**CRITICAL**: Only stage items. NEVER execute final payment without explicit "CONFIRM BUY" approval.

1. **Open Grocery Service**: Use Latch browser to navigate to Amazon Fresh (or configured service)
2. **Search & Add**: Search for recommended items, add to cart
3. **Navigate to Checkout**: Go to cart review page, DO NOT proceed to payment
4. **Send Approval Request** via Plow Chat:
   ```
   ⚠️ Protein deficit detected (3 days < target).
   
   Staged in Amazon cart:
   - 2x Fage Greek Yogurt 0% (500g) - $6.98 each
   - 1x Optimum Whey Isolate (2lb) - $39.99
   
   Total: $53.95 (before tax)
   
   Items ready for checkout. Reply 'CONFIRM BUY' to complete purchase.
   ```

5. **Wait for Approval**: Do NOT click "Place Order" or final payment button
6. **On "CONFIRM BUY" Response**: Execute final payment click, verify order confirmation, send receipt screenshot

## Approval Gate

Absolutely **FORBIDDEN** to execute payment without exact phrase "CONFIRM BUY" from user.

Any other response:
- "CANCEL": Remove items from cart, confirm cancellation
- "CHANGE": Ask what to modify, update cart, re-request approval
- No response after 24h: Send reminder, do NOT auto-purchase

## Post-Purchase

After successful order:
1. Screenshot order confirmation
2. Note order number and delivery date
3. Send confirmation SMS with screenshot
4. Update grocery staging log to prevent duplicate staging

## Error Handling

- If grocery service unavailable: Report, suggest manual order
- If items out of stock: Suggest alternatives, re-request approval
- If payment fails: Report error, do NOT retry without user instruction
- If cart was cleared: Re-stage and re-request approval
