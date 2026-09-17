# Closing Investigation Skill

## Purpose

The Closing Investigation skill enables AURA Agent to diagnose, investigate, and reconcile end-of-day discrepancies in Daily Closing across Cash Closing and Inventory Closing.

Questions answered:
- Why is there a cash shortage or overage in the cashier drawer closing?
- What caused the inventory variance between expected closing stock and physical count?
- Did unrecorded sales, display transfers, or delayed receiving entries cause the discrepancy?
- Does the discrepancy represent a mathematical error, timing lag, or unrecorded transaction?

This skill reconstructs shift reconciliation ledgers. It does not accuse personnel of misconduct or automatically adjust cash or inventory records.

---

## When to Use

Use when investigating discrepancies arising during Daily Closing:

### Cash Closing Discrepancies
- "Why is Register 1 short Rp 35,000 in today's closing?"
- "What caused the cash overage in the afternoon shift closing?"
- "Did voided transactions explain the register drawer variance?"

### Inventory Closing Discrepancies
- "Why did daily closing report a -4 unit variance for Bango Kecap?"
- "What caused the discrepancy between physical display count and expected stock?"
- "Did receiving completed during shift get included in today's closing formula?"

### Shift Audits
- "Review closing accuracy and variance patterns for Cashier A this week."

---

## When Not to Use

Route non-closing inquiries to their specialized skills:
- Comprehensive full-store periodic physical counts → `inventory_analysis` or `anomaly_investigation`
- Persistent multi-week dead stock or shrinkage analysis → `anomaly_investigation`
- Stockout burn rate and replenishment runout timing → `stockout_investigation`
- Standard sales revenue analytics without register reconciliation → `sales_analysis`
- Generating purchase orders for restocking → `reorder_recommendation`

---

## Required Context

Identify before investigating:
- Closing Domain: Cash Closing (Cashier drawer) vs Inventory Closing (Warehouse SKU counts)
- Session Metadata: Date, shift, register ID, cashier/staff ID
- Mathematical Components:
  - *Cash Closing*: Expected Cash, Actual Cash, Variance (`Actual - Expected`)
  - *Inventory Closing*: Opening Stock, Receivings (+), Sales (-), Movements (+/-), Expected Stock, Physical Count (`Display + On-Hand`), Variance (`Physical - Expected`)
- Shift Ledgers: Sales receipts, void logs, receiving logs, movement records, audit trail

---

## MCP Tools

Use only authorized PRD tools:

### READ Tools
- `get_daily_closing`: Fetch submitted closing reports, counts, expected balances, and statuses.
- `get_sales_history`: Review cash transaction receipts, payment methods, and timestamps.
- `get_inventory`: Fetch current stock balances and Display/On-Hand splits.
- `get_inventory_movements`: Review transfers, write-offs, and adjustments during shift.
- `get_receivings`: Cross-check deliveries received and confirmed during shift.
- `get_audit_logs`: Inspect supervisor overrides, price changes, and voided receipts.

### ANALYZE Tools
- `analyze_closing_variance`: Evaluate overall closing session accuracy and thresholds.
- `analyze_cash_variance`: Diagnose ticket math, change calculation errors, and cash flow patterns.
- `analyze_inventory_variance`: Deconstruct the inventory closing formula ledger.

### RECOMMEND Tools
- `generate_inventory_action`: Propose recount procedures or physical spot-checks.
- `generate_business_insight`: Summarize recurring closing variances for Owner review.

---

## Reasoning Procedure

1. **Classify Closing Domain**: Determine whether investigating Cash Closing or Inventory Closing.
2. **Establish Numerical Discrepancy**:
   - Cash: `Cash Variance = Actual Cash - Expected Cash` (Negative = Shortage, Positive = Overage).
   - Inventory:
```text
Expected Stock = Opening Stock + Receivings - Sales ± Adjustments ± Movements
Inventory Variance = Physical Closing Stock - Expected Stock
```
3. **Reconstruct Shift Ledger**:
   - Cash: Reconcile opening float + cash receipts - cash payouts.
   - Inventory: Reconcile opening balance + shift receipts - POS sales ± logged transfers.
4. **Cross-Check Audit Records**:
   - Inspect `get_audit_logs` for voided receipts, canceled items, or manual drawer opens.
   - Inspect `get_receivings` to verify if receiving completed before or after physical count.
5. **Formulate Possible Causes**:
   - *Timing Mismatch*: Receiving logged in system after physical count was taken.
   - *Omission*: Display transfer physically executed but unlogged in system.
   - *Cash Handling Error*: Incorrect change returned to customer or miscounted drawer.
   - *Unreconciled Variance*: Difference remains unexplained after checking ledgers.
6. **Assign Confidence**: High if records explain the exact difference; Unknown if unrecorded.

---

## Evidence Requirements

| Discrepancy Claim | Required MCP Evidence |
| :--- | :--- |
| Cash Closing Variance | `get_daily_closing` recorded cash variance amount |
| Voided Receipt Explains Cash Gap | `get_audit_logs` void timestamp matches variance amount |
| Receiving Timing Discrepancy | `get_receivings` timestamp postdates physical count timestamp |
| Unrecorded Transfer Discrepancy | Display count is short while On-Hand count is surplus by identical amount |

Strict Rule on Misconduct:
Never allege theft or intentional misconduct without conclusive audit documentation. Label unexplained deficits as "Unreconciled Cash Shortage" or "Unreconciled Inventory Variance".

If cause cannot be proven:
> "Cause could not be determined from available data."

---

## Uncertainty Handling

- **Uncounted SKUs**: Daily inventory closing counts selected samples, not the entire catalog. Do not extrapolate partial closing variances to uncounted store inventory.
- **Drawer Float Gaps**: If opening register drawer float was not recorded at shift start, state that baseline cash carries uncertainty.

---

## Output Format

```markdown
## Finding
[Concise statement of closing discrepancy and net variance]

## Closing Discrepancy Profile
- Closing Type: [Cash Closing | Inventory Closing]
- Session / Shift: [Date, Shift, Register / Staff ID]
- Expected Amount / Count: [System Expected value]
- Actual Amount / Count: [Physical Counted value]
- Net Variance: [+/- Amount or Units]

## Evidence & Reconciliation
[Itemized ledger reconciliation comparing sales, movements, and audit records]

## Possible Cause
[Evidence-grounded explanation: timing mismatch, change error, or unrecorded movement]

## Confidence
[HIGH | MEDIUM | LOW | UNKNOWN] — [Brief justification]

## Operational Recommendation
[Recommended human action: recount, supervisor review, or adjustment decision]
```

---

## Examples

### Example 1: Cash Closing Shortage via Voided Transaction

```markdown
## Finding
Register 1 recorded a cash shortage of Rp 25,000 during the evening closing on 2026-09-11.

## Closing Discrepancy Profile
- Closing Type: Cash Closing (Cashier: Budi, Register 1)
- Session / Shift: 2026-09-11 (14:00–22:00 Shift)
- Expected Cash: Rp 2,450,000
- Actual Cash Count: Rp 2,425,000
- Net Variance: -Rp 25,000 (Shortage)

## Evidence & Reconciliation
- Recorded cash sales: Rp 2,150,000 across 68 transactions (`get_sales_history`).
- Opening float: Rp 300,000.
- `get_audit_logs` records 1 supervisor void at 20:15 for Transaction #TX-9912 (value: Rp 25,000).
- Cashier accepted cash, customer canceled, cashier re-scanned without immediate cancel, creating drawer count mismatch.

## Possible Cause
Change handling confusion during voided transaction #TX-9912 created an uncollected Rp 25,000 discrepancy.

## Confidence
HIGH — Audit log entry matches the exact Rp 25,000 variance amount.

## Operational Recommendation
Supervisor should review void procedures with cashier. Owner may log variance resolution.
```

### Example 2: Inventory Closing Variance via Receiving Timing Lag

```markdown
## Finding
Pocari Sweat 500ml showed a closing variance of -24 units during warehouse evening closing.

## Closing Discrepancy Profile
- Closing Type: Inventory Closing
- Session / Shift: 2026-09-11 Warehouse Closing
- Expected Closing Stock: 48 units
- Physical Closing Count: 24 units (Display: 12, On-Hand: 12)
- Net Variance: -24 units

## Evidence & Reconciliation
- Opening Stock: 24 units; Sales during shift: 0 units.
- Expected stock was 48 units because receiving RC-2026-041 (24 units) was submitted in system at 16:30 (`get_receivings`).
- Physical warehouse count was completed at 16:15, before the shipment was unloaded.

## Possible Cause
Timing mismatch; system receiving was completed after the physical count took place.

## Confidence
HIGH — Corroborated by timestamp sequence (`Physical Count 16:15 < Receiving Entry 16:30`).

## Operational Recommendation
Warehouse Admin should confirm the 24 units are in storage. No inventory adjustment needed.
```

---

## What This Skill Must Never Do

- Never accuse employees of theft or dishonesty without proof.
- Never automatically approve closing reports or apply inventory adjustments.
- Never modify audit logs or delete transaction histories.
- Never invent drawer float values, physical counts, or transaction numbers.
- Never bypass the MCP gateway to access PostgreSQL directly.

---

## Relationship With Other Skills

```text
               closing_investigation
                         │
     ┌───────────────────┼───────────────────┐
     ▼                   ▼                   ▼
sales_analysis     inventory_analysis    anomaly_investigation
(Reconciles cash   (Verifies physical    (Receives handoff if
 receipts math)     counts & movements)   variance is chronic)
```

- `sales_analysis`: Provides sales receipt totals and cash payment verification.
- `inventory_analysis`: Provides inventory movement ledgers and stock counts.
- `anomaly_investigation`: Investigates systemic, chronic variances across shifts.

---

## Reasoning Checklist

- [ ] Did I establish exact Expected, Actual, and Variance numbers?
- [ ] Did I verify the inventory closing formula (`Opening + In - Out ± Moves`)?
- [ ] Did I check `get_audit_logs` for voided receipts, refunds, or overrides?
- [ ] Did I verify timestamp ordering between physical counts and system entries?
- [ ] Did I refrain from making accusations of theft or dishonesty?
- [ ] Did I use the standard limitation phrase if cause cannot be proven?
- [ ] Did I avoid modifying system balances or approving closings autonomously?

---

## Final Principle

Closing investigation reconciles shift ledgers against physical reality. AURA Agent calculates the mathematics, reconstructs the timeline, and highlights discrepancies; human managers review findings and decide corrective actions.
