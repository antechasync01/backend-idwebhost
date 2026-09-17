# Stockout Investigation Skill

## Purpose

The Stockout Investigation skill enables AURA Agent to diagnose why a product stocked out (retrospective) or evaluate imminent stockout risk (prospective). It correlates sales velocity, inventory movements, and supplier deliveries into operational intelligence.

Questions answered:
- Why did this product run out of stock?
- When will this product run out of stock at current velocity?
- Is stockout caused by demand surge, delivery delay, or unrecorded movement?
- Is the issue a store-wide stockout or merely an empty display shelf?

This skill investigates causes and assesses risks. It does not execute purchases or modify inventory.

---

## When to Use

Use when the inquiry centers on depleted inventory or critical runout risk:

### Retrospective Depletion
- "Why did Aqua 600ml run out of stock yesterday?"
- "What caused the stockout for Indomie Goreng this weekend?"
- "Did sales spike or did a delivery fail to arrive?"

### Prospective Risk Assessment
- "Which fast-moving products will run out before Friday?"
- "How many days of stock remain for Ultra Milk Chocolate?"
- "Is this product at high risk of stockout given current burn rate?"

### Shelf vs Storage Diagnostics
- "Why does the POS say out of stock when we supposedly have units?"
- "Is the sales floor empty while warehouse stock remains?"

---

## When Not to Use

Route other intents to their specialized skills:
- Checking general inventory levels → `inventory_analysis`
- Pure forward-looking demand forecasting → `demand_forecasting`
- Calculating optimal reorder quantity and order proposals → `reorder_recommendation`
- Selecting and contacting suppliers → `supplier_recommendation`
- Inventory discrepancy without velocity context → `inventory_analysis` or `anomaly_investigation`
- Register or cash closing discrepancies → `closing_investigation`

---

## Required Context

Identify before investigating:
- Product identity: Name, SKU, or EAN-13 barcode
- Mode: Retrospective (already out) vs Prospective (risk of running out)
- Inventory breakdown: Display Stock, On-Hand Stock, Total Available
- Sales velocity: Average daily sales (burn rate)
- Operational pipeline: Pending receivings, recent transfers, recent adjustments

---

## MCP Tools

Use only PRD-defined tools:

### READ Tools
- `get_inventory`: Fetch Display, On-Hand, and Total Available stock.
- `get_inventory_movements`: Check timestamped adjustments, sales, and transfers.
- `get_sales_history`: Analyze transaction volume and sales acceleration.
- `get_receivings`: Inspect completed, scheduled, or delayed deliveries.
- `get_product` / `get_products`: Retrieve product catalog metadata.
- `get_upcoming_events`: Identify demand triggers (holidays, local events).

### ANALYZE Tools
- `calculate_stockout_risk`: Compute days to stockout and risk category.
- `forecast_demand`: Project forward sales velocity under trend/event conditions.

### RECOMMEND Tools
- `generate_inventory_action`: Propose internal fixes (e.g., display restock).
- `generate_reorder_recommendation`: Trigger formal replenishment evaluation.

---

## Reasoning Procedure

1. **Classify Mode**: Determine if investigating past stockout (`total_available == 0`) or prospective risk (`days_to_stockout <= threshold`).
2. **Verify Stock Split**: Check `Display Stock + On-Hand Stock = Total Available`. Determine if store-wide (`Total == 0`) or display-only (`Display == 0`, `On-Hand > 0`).
3. **Calculate Velocity**: Query `get_sales_history` and `calculate_stockout_risk` to find daily burn rate and recent velocity changes.
4. **Reconstruct Depletion Timeline**:
```text
Opening Stock → Sales Velocity → Supplier Receiving → Internal Movement → Depletion Point
```
5. **Evaluate Drivers**:
   - *Demand Surge*: Sales exceeded historical average (> 1.5x baseline).
   - *Receiving Delay*: Scheduled supplier delivery missed or delayed.
   - *Display Shelf Gap*: Stock exists in warehouse but was not moved to display.
   - *Unexplained Loss*: Stock dropped without sales records (route to `anomaly_investigation`).
6. **Formulate Output**: Separate facts from inferences. Assign confidence.

---

## Evidence Requirements

| Finding Claim | Required MCP Evidence |
| :--- | :--- |
| Product is stocked out | `get_inventory` shows `total_available == 0` |
| Product at stockout risk | `calculate_stockout_risk` shows `days_to_stockout <= threshold` |
| Demand surge caused stockout | `get_sales_history` shows sales > 1.5x baseline average |
| Supplier delay contributed | `get_receivings` records expected delivery not fulfilled |
| Display-only shortage | `get_inventory` shows `display_stock == 0` and `on_hand_stock > 0` |

If causal evidence is absent, state:
> "Cause could not be determined from available data."

---

## Uncertainty Handling

- **Limited History**: If sales data spans fewer than 7 days, state burn rate is provisional and cap confidence at MEDIUM.
- **Missing Delivery Logs**: If supplier delivery schedules are absent, do not assume supplier fault; note missing receiving logs.
- **Stockout Blind Spot**: If recorded sales dropped to zero, check if product was stocked out rather than demand declining.

---

## Output Format

```markdown
## Finding
[Concise summary of stockout condition or risk status]

## Inventory Status
- Display Stock: [X] units
- On-Hand Stock: [Y] units
- Total Available: [Z] units
- Daily Burn Rate: [D] units/day
- Estimated Days to Stockout: [N] days (if prospective)

## Evidence & Timeline
[Chronological facts established from MCP tools]

## Possible Cause
[Evidence-supported explanation of depletion drivers]

## Confidence
[HIGH | MEDIUM | LOW | UNKNOWN] — [Brief justification]

## Operational Recommendation
[Recommended human action: shelf transfer, reorder review, or investigation]
```

---

## Examples

### Example 1: Retrospective Stockout via Demand Surge

```markdown
## Finding
Aqua 600ml stocked out on 2026-09-11 at 18:30 due to a demand surge.

## Inventory Status
- Display Stock: 0 units
- On-Hand Stock: 0 units
- Total Available: 0 units
- Normal Burn Rate: 12 units/day

## Evidence & Timeline
- 2026-09-11 08:00: Opening stock was 28 units (`get_inventory`).
- 2026-09-11 12:00–17:00: Sold 26 units across 8 transactions (`get_sales_history`), coinciding with a nearby community marathon.
- 2026-09-11 18:30: Last 2 units sold. Stockout confirmed.
- No delivery was scheduled for this date (`get_receivings`).

## Possible Cause
Demand surge (233% of daily average in 6 hours) depleted inventory prior to regular weekly replenishment.

## Confidence
HIGH — Direct sales timestamps and inventory movements confirm timeline.

## Operational Recommendation
Owner should evaluate restocking via `reorder_recommendation` and note event impact for future scheduling.
```

### Example 2: False Total Stockout (Display Shelf Empty)

```markdown
## Finding
Teh Botol Sosro 450ml is missing from shelves, but 48 units remain in warehouse storage.

## Inventory Status
- Display Stock: 0 units
- On-Hand Stock: 48 units
- Total Available: 48 units

## Evidence & Timeline
- Cashier reported product missing from shelf.
- `get_inventory` confirms Display Stock is 0, while On-Hand Stock is 48.
- `get_inventory_movements` shows last display transfer occurred 4 days ago.

## Possible Cause
Internal display replenishment gap; warehouse stock was not transferred to retail display.

## Confidence
HIGH — Verified backend inventory split.

## Operational Recommendation
Warehouse staff should perform a Display Transfer of 24 units immediately. No external reorder required.
```

---

## What This Skill Must Never Do

- Never execute purchase orders or supplier orders.
- Never modify inventory balances or generate automated stock adjustments.
- Never confuse zero display stock with total store stockout.
- Never allege theft or misconduct without conclusive audit records.
- Never invent sales rates, delivery dates, or stockout timestamps.
- Never bypass the MCP gateway to access PostgreSQL directly.

---

## Relationship With Other Skills

```text
               stockout_investigation
                     │
     ┌───────────────┼───────────────┐
     ▼               ▼               ▼
inventory_analysis  demand_forecasting  reorder_recommendation
(Stock breakdown    (Projected sales    (Handoff to evaluate
 & movement logs)    under events)       restock orders)
```

- `inventory_analysis`: Supplies base stock split (Display, On-Hand, Total).
- `demand_forecasting`: Supplies projected demand when sales patterns shift.
- `reorder_recommendation`: Receives handoff when stockout requires purchasing.
- `anomaly_investigation`: Receives handoff when depletion occurred without recorded sales.

---

## Reasoning Checklist

- [ ] Did I verify Display Stock, On-Hand Stock, and Total Available?
- [ ] Did I distinguish retrospective depletion from prospective runout risk?
- [ ] Did I check delivery records via `get_receivings`?
- [ ] Is burn rate derived from recorded sales data?
- [ ] Did I label unverified causal relationships as "Possible Cause"?
- [ ] If data cannot establish cause, did I use the standard limitation phrase?
- [ ] Did I avoid claiming to execute orders or adjust stock?

---

## Final Principle

Stockout investigation exists to diagnose why stock depleted or when it will run out. AURA Agent analyzes the facts, reconstructs the timeline, and presents operational recommendations; human owners and staff retain all purchasing and stock adjustment authority.
