# Anomaly Investigation Skill

## Purpose

The Anomaly Investigation skill enables AURA Agent to detect, investigate, and explain operational anomalies across sales, inventory, and warehouse activities. It distinguishes genuine operational irregularities from normal fluctuations, data errors, or external disruptions.

Questions answered:
- Why did sales drop or spike abruptly without price or catalog changes?
- Why did stock decrease without corresponding POS sales transactions?
- Why has a product with high warehouse stock recorded zero sales (dead stock)?
- What caused an unusual inventory movement pattern or negative variance?

This skill explains operational divergence through cross-domain evidence. It does not perform inventory write-offs or make accusations of misconduct.

---

## When to Use

Use when an operational metric diverges significantly from historical patterns or system logic:

### Sales Anomalies
- "Why did Indomie sales collapse 85% this week compared to last week?"
- "Is this sudden 400% sales spike on cooking oil an anomaly?"
- "Which products recorded zero sales for 20 days despite available stock?"

### Inventory Anomalies
- "Why did 12 units of shampoo disappear without recorded sales?"
- "Why did stock increase without a receiving record?"
- "Why does physical display stock show repeated unrecorded adjustments?"

### Operational Inactivity
- "Which fast-moving products have stagnated in the warehouse without shelf transfers?"
- "Are there products with active inventory but zero transaction activity?"

---

## When Not to Use

Route non-anomalous inquiries to their respective domains:
- Routine sales trends and standard period comparisons → `sales_analysis`
- General inventory inquiries and stock distribution → `inventory_analysis`
- End-of-day register cash or inventory closing discrepancies → `closing_investigation`
- Expected inventory exhaustion and burn rate calculations → `stockout_investigation`
- Future demand projections under normal conditions → `demand_forecasting`

---

## Required Context

Identify before investigating:
- Anomaly Category: Sales anomaly, inventory shrinkage/drift, or dead stock
- Target Entity: Product, category, or operational period
- Operational Baseline: Normal moving average sales, expected stock trajectory, or standard receiving cycle
- Cross-Domain Records: Movement logs, POS transactions, supplier receivings, audit trails

---

## MCP Tools

Use only authorized PRD tools:

### READ Tools
- `get_sales_history`: Review transaction records and velocity.
- `get_inventory`: Check current Display Stock, On-Hand Stock, and Total Available.
- `get_inventory_movements`: Inspect timestamped adjustments, transfers, and deductions.
- `get_receivings`: Verify supplier delivery dates, quantities, and statuses.
- `get_audit_logs`: Examine system changes, manual overrides, and user actions.
- `get_entity_history`: Trace historical state transitions of the target product.
- `get_weather_context` / `get_upcoming_events`: Identify external disruptors (storms, holidays).

### ANALYZE Tools
- `detect_sales_anomalies`: Detect velocity drops, surges, and dead stock.
- `detect_inventory_anomalies`: Identify unexplained variances, negative drift, and shrinkage.
- `analyze_inventory_variance`: Quantify differences between expected and actual counts.

### RECOMMEND Tools
- `generate_inventory_action`: Recommend physical checks, display transfers, or audit reviews.
- `generate_business_insight`: Summarize recurring anomalous patterns for Owner attention.

---

## Reasoning Procedure

1. **Verify Deviation Against Baseline**: Compare observed metric with baseline historical norm (e.g., 14-day average). Confirm departure exceeds statistical noise.
2. **Classify Anomaly Nature**:
   - *Volume Anomaly*: Sudden surge or drop in sales.
   - *Flow Discrepancy*: Stock change without corresponding POS sale or receiving.
   - *Operational Friction*: Stock in warehouse never transferred to retail display.
3. **Cross-Domain Correlation**:
```text
Sales Record ───(compare)─── Inventory Movement ───(verify)─── Audit Trail
```
   - If stock dropped, does a matching sales receipt exist in `get_sales_history`?
   - If stock increased, does an approved receiving record exist in `get_receivings`?
   - If sales ceased, is Display Stock 0 while On-Hand Stock is positive?
4. **Isolate External Factors**: Query `get_weather_context` and `get_upcoming_events` to test if external events explain unusual patterns.
5. **Formulate Possible Causes**: Distinguish verified facts from possible explanations.
6. **Assign Confidence**: Calibrate confidence based on audit log and transaction completeness.

---

## Evidence Requirements

| Anomaly Type | Required MCP Evidence |
| :--- | :--- |
| Unmatched Stock Reduction | `get_inventory_movements` shows decrease without matching `get_sales_history` transaction IDs |
| Dead Stock with Display Gap | `get_inventory` shows `display_stock == 0` and `on_hand_stock > 0` during zero-sales window |
| Abrupt Demand Drop | `detect_sales_anomalies` confirms drop > 3 standard deviations below baseline |
| Unrecorded Inventory Influx | Stock increased without corresponding approved receiving in `get_receivings` |

Rule on Causality:
Never assert theft, fraud, or intentional misconduct without conclusive audit documentation. Label unexplained inventory gaps as "Unmatched Physical Variance".

If cause cannot be proven:
> "Cause could not be determined from available data."

---

## Uncertainty Handling

- **Gaps in Audit Trail**: If audit logging is incomplete for the target timeframe, note that human actions cannot be verified and cap confidence at LOW.
- **Stockout vs Demand Collapse**: When sales drop to zero, verify whether inventory was available. Zero sales of an out-of-stock item is an inventory issue, not a sales anomaly.

---

## Output Format

```markdown
## Finding
[Concise description of the detected operational anomaly]

## Anomaly Profile
- Target Entity: [Product Name / Category]
- Normal Baseline: [Historical rate or expected count]
- Observed Value: [Actual recorded value]
- Deviation: [Percentage or unit difference]

## Evidence & Timeline
[Timestamped facts established from sales, movements, and audit records]

## Possible Cause
[Evidence-grounded explanation of operational divergence]

## Confidence
[HIGH | MEDIUM | LOW | UNKNOWN] — [Brief justification]

## Operational Recommendation
[Recommended human action: physical stock opname, display transfer, or audit check]
```

---

## Examples

### Example 1: Unmatched Inventory Decrease (Shrinkage Signal)

```markdown
## Finding
Bango Kecap Manis 550ml experienced an unrecorded reduction of 8 units between 2026-09-10 and 2026-09-11.

## Anomaly Profile
- Target Entity: Bango Kecap Manis 550ml (SKU: BNG-550)
- Normal Baseline: 24 units expected balance
- Observed Value: 16 units physical count
- Deviation: -8 units (-33.3% variance)

## Evidence & Timeline
- 2026-09-10 21:00: Recorded balance was 24 units (Display: 12, On-Hand: 12).
- 2026-09-11 08:00–20:00: `get_sales_history` recorded only 2 units sold.
- 2026-09-11 21:00: Daily check recorded total available stock as 16 units.
- `get_inventory_movements` contains no transfer, breakage, or return entries.
- `get_audit_logs` shows no manual adjustments performed.

## Possible Cause
Unmatched physical variance; 6 units left the inventory without corresponding sales or adjustment records.

## Confidence
HIGH for variance occurrence; UNKNOWN for specific physical root cause.

## Operational Recommendation
Warehouse Admin should conduct a spot stock opname for Bango Kecap Manis and review storage access logs.
```

### Example 2: Dead Stock Caused by Shelf Neglect

```markdown
## Finding
Tolak Angin Cair has recorded zero sales for 18 consecutive days despite 60 units held in store inventory.

## Anomaly Profile
- Target Entity: Tolak Angin Cair 15ml
- Normal Baseline: 4.5 units/day historical average
- Observed Value: 0 units/day over past 18 days
- Deviation: -100% sales activity

## Evidence & Timeline
- `get_inventory` reveals: Display Stock = 0 units, On-Hand Stock = 60 units.
- `get_inventory_movements` indicates last Display Transfer occurred 22 days ago.
- Product has been absent from customer display shelves since 2026-08-25.

## Possible Cause
Display neglect; product was physically unavailable to shoppers despite warehouse inventory.

## Confidence
HIGH — Directly corroborated by zero display stock and stagnant on-hand balance.

## Operational Recommendation
Perform a Display Transfer of 20 units to customer display immediately.
```

---

## What This Skill Must Never Do

- Never accuse personnel of theft or misconduct without explicit audit confirmation.
- Never execute automated inventory balance corrections or write-offs.
- Never dismiss anomalies without checking cross-domain evidence.
- Never invent baseline statistics, scan records, or audit events.
- Never bypass the MCP gateway to access PostgreSQL directly.

---

## Relationship With Other Skills

```text
               anomaly_investigation
                        │
     ┌──────────────────┼──────────────────┐
     ▼                  ▼                  ▼
sales_analysis    inventory_analysis   closing_investigation
(Normal sales     (Stock balance &     (End-of-day register
 trends baseline)  movement verification) and cash variance)
```

- `sales_analysis`: Provides historical sales velocity to establish normal behavior.
- `inventory_analysis`: Validates current stock splits and movement ledger.
- `closing_investigation`: Receives handoff if anomaly is tied to end-of-day closing.
- `stockout_investigation`: Engaged if anomaly directly precipitates a stockout event.

---

## Reasoning Checklist

- [ ] Did I establish a verified numerical baseline rather than an assumption?
- [ ] Did I compare sales records against inventory movements?
- [ ] Did I check if zero sales were caused by zero display stock?
- [ ] Did I review `get_audit_logs` for manual adjustments or overrides?
- [ ] Did I refrain from making accusations of theft or misconduct?
- [ ] Did I use the canonical phrase if root cause cannot be established?
- [ ] Did I avoid claiming to modify system balances?

---

## Final Principle

Anomaly investigation detects and explains operational divergence without conjecture. AURA Agent reconstructs the factual ledger across sales, movement, and audit data, empowering human managers to resolve discrepancies with accountability.
