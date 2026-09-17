# Reorder Recommendation Skill

## Purpose

The Reorder Recommendation skill enables AURA Agent to analyze inventory levels, consumption velocity, and supplier lead times to recommend optimal replenishment quantities and reorder priorities.

Questions answered:
- Which products need to be reordered today?
- How many units of Product X should we order from the supplier?
- What is the stockout risk if replenishment is delayed?
- Which supplier provides this product and what is their contact?
- How do pending deliveries affect current replenishment calculations?

This skill provides actionable replenishment advice. It never executes purchase orders, sends orders to suppliers, or commits store funds.

---

## When to Use

Use when the user seeks replenishment advice, order quantities, or reorder urgency:

### Active Replenishment Requests
- "What products should I reorder today?"
- "How much Indomie Goreng should we order for next week?"
- "Recommend reorder quantity for Aqua 600ml."

### Buffer & Risk Evaluations
- "Which low-stock items require immediate purchase orders?"
- "How many days of stock do we have left before we must place an order?"
- "Will our pending shipment cover expected demand?"

---

## When Not to Use

Route non-replenishment inquiries to their appropriate skills:
- Executing purchase orders or placing supplier orders → External Manual Task (Owner responsibility)
- Comparing multiple suppliers on price, terms, or contact options → `supplier_recommendation`
- Diagnosing why a stockout occurred in the past → `stockout_investigation`
- Pure forward demand projections without order sizing → `demand_forecasting`
- General inventory checks and warehouse counts → `inventory_analysis`

---

## Required Context

Identify before calculating recommendations:
- Target Product: SKU, name, or product category
- Current Stock Split: Display Stock, On-Hand Stock, Total Available
- Active Pipeline: Pending receivings or scheduled shipments
- Daily Burn Rate: Average daily sales (ADS) from sales history
- Supplier Parameters: Supplier name, contact details, and estimated lead time
- Target Coverage: Days of desired inventory buffer (e.g., 7 or 14 days)

---

## MCP Tools

Use only authorized PRD tools:

### READ Tools
- `get_inventory`: Retrieve current Display Stock, On-Hand Stock, and Total Available.
- `get_sales_history`: Compute historical sales velocity and daily burn rate.
- `get_receivings`: Inspect pending or in-transit supplier deliveries.
- `get_product` / `get_products`: Retrieve product metadata, category, and pack sizes.
- `get_supplier` / `get_supplier_products`: Identify linked supplier and contact info.

### ANALYZE Tools
- `calculate_stockout_risk`: Evaluate runout horizon and urgency tier.
- `forecast_demand`: Project forward consumption during lead time and cycle period.

### RECOMMEND Tools
- `generate_reorder_recommendation`: Calculate optimal reorder quantity and safety buffer.
- `generate_supplier_contact_recommendation`: Propose supplier contact actions.

---

## Reasoning Procedure

1. **Establish Effective Inventory Position**:
```text
Net Inventory = Total Available (Display + On-Hand) + Pending Receivings
```
   Always include pending receivings to prevent duplicate reorders.
2. **Determine Daily Burn Rate & Lead Time**:
   - Query `get_sales_history` to calculate Average Daily Sales (ADS).
   - Retrieve supplier lead time (e.g., 2 days) from supplier records or historical receiving logs.
3. **Assess Runout Horizon & Urgency**:
   - Calculate Days of Supply: `Days to Stockout = Net Inventory / ADS`.
   - *CRITICAL*: Days to Stockout <= Supplier Lead Time (immediate order needed).
   - *HIGH*: Days to Stockout <= Lead Time + 2 days safety buffer.
   - *NORMAL*: Days to Stockout > Target Review Cycle.
4. **Calculate Recommended Order Quantity**:
```text
Order Quantity = (Demand during Lead Time + Target Coverage Demand) - Net Inventory
```
   Round to carton or pack multiples when standard packaging is defined.
5. **Identify Supplier Contact**:
   Call `get_supplier_products` to match the product to its active supplier and retrieve WhatsApp/phone details.
6. **Formulate Recommendation**: Clearly distinguish recommendation from execution. Direct the Owner to place the external order.

---

## Evidence Requirements

| Recommendation Component | Required MCP Evidence |
| :--- | :--- |
| Current Stock Position | `get_inventory` confirmed balances |
| Pending Deliveries | `get_receivings` checked for in-transit orders |
| Daily Burn Rate | `get_sales_history` or `calculate_stockout_risk` |
| Supplier Match | `get_supplier_products` active supplier link |

Core Rule:
Never state that an order has been placed. Use:
> "I recommend ordering [X] units from [Supplier]."

---

## Uncertainty Handling

- **Unknown Lead Time**: If supplier lead time is not explicitly recorded, assume a conservative 2-day lead time and declare the assumption clearly.
- **Unstable Demand**: If sales velocity fluctuates widely, provide a recommended range (e.g., 40–50 units) and state the volatility factor.

---

## Output Format

```markdown
## Recommendation Summary
[Concise summary of recommended replenishment action]

## Inventory & Velocity Profile
- Display Stock: [X] units
- On-Hand Stock: [Y] units
- Total Available: [Z] units
- Pending Inbound: [P] units (Expected: [Date])
- Net Available Position: [Z + P] units
- Daily Burn Rate: [D] units/day
- Days of Supply Remaining: [N] days

## Recommended Action
- Recommended Order: [Q] units (or [C] cartons)
- Urgency Level: [CRITICAL | HIGH | NORMAL]
- Target Supplier: [Supplier Name] (Contact: [Phone / WhatsApp])
- Target Coverage: [N] days of operational supply

## Evidence & Calculation
[Brief explanation of formula: Lead Time Demand + Coverage Buffer - Net Position]

## Confidence
[HIGH | MEDIUM | LOW | UNKNOWN] — [Brief justification]

## Owner Action Required
[Step-by-step reminder that purchasing is executed externally by Owner]
```

---

## Examples

### Example 1: Critical Reorder for Fast-Moving Beverage

```markdown
## Recommendation Summary
Aqua 600ml requires an immediate replenishment order of 48 units (2 cartons) to avoid weekend stockout.

## Inventory & Velocity Profile
- Display Stock: 6 units
- On-Hand Stock: 8 units
- Total Available: 14 units
- Pending Inbound: 0 units (`get_receivings`)
- Daily Burn Rate: 9.5 units/day (`get_sales_history`)
- Days of Supply Remaining: ~1.5 days

## Recommended Action
- Recommended Order: 48 units (2 cartons of 24)
- Urgency Level: CRITICAL (exhaustion projected within 36 hours)
- Target Supplier: PT Sumber Tirta Lestari (WhatsApp: 0812-3456-7890)
- Target Coverage: 5 days of operational buffer

## Evidence & Calculation
- Lead time is 1 day (consumption during lead time: ~10 units).
- Target 5-day cycle requires 48 units.
- Net inventory of 14 units will be exhausted before Friday evening without reorder.

## Confidence
HIGH — Verified stock count and consistent daily sales rate.

## Owner Action Required
Owner should contact PT Sumber Tirta Lestari via WhatsApp to place the order externally. Once goods arrive, Warehouse Staff will record receiving.
```

### Example 2: Normal Reorder Screening

```markdown
## Recommendation Summary
Indomie Goreng Special is scheduled for routine weekly reorder of 80 units (2 boxes).

## Inventory & Velocity Profile
- Display Stock: 15 units
- On-Hand Stock: 25 units
- Total Available: 40 units
- Pending Inbound: 0 units
- Daily Burn Rate: 8.0 units/day
- Days of Supply Remaining: 5.0 days

## Recommended Action
- Recommended Order: 80 units (2 boxes of 40)
- Urgency Level: NORMAL (5 days buffer remaining)
- Target Supplier: CV Pangan Sejahtera (Phone: 021-555-1234)
- Target Coverage: 10 days of operational buffer

## Evidence & Calculation
Lead time is 2 days (16 units consumed). Order placed now will arrive with ~24 units buffer remaining, maintaining healthy stock.

## Confidence
HIGH — Stable burn rate and clear supplier catalog link.

## Owner Action Required
Owner should include this item in the regular weekly supplier order.
```

---

## What This Skill Must Never Do

- Never execute purchase orders, contracts, or financial payments.
- Never send automated messages or purchase commitments to suppliers.
- Never ignore pending receivings, causing duplicate order recommendations.
- Never modify inventory balances or safety stock parameters directly.
- Never bypass the MCP gateway to access PostgreSQL directly.

---

## Relationship With Other Skills

```text
              reorder_recommendation
                        │
     ┌──────────────────┼──────────────────┐
     ▼                  ▼                  ▼
stockout_investigation demand_forecasting supplier_recommendation
(Triggers reorder      (Provides future   (Supplies contact &
 on runout risk)        demand velocity)   supplier comparisons)
```

- `stockout_investigation`: Identifies depleted stock requiring replenishment.
- `demand_forecasting`: Projects forward sales velocity under events or holidays.
- `supplier_recommendation`: Provides detailed supplier profiles, catalog links, and communication options.

---

## Reasoning Checklist

- [ ] Did I calculate Net Inventory by including pending receivings?
- [ ] Did I verify supplier lead time or state reasonable assumptions?
- [ ] Is recommended quantity based on recorded burn rate?
- [ ] Did I match the correct supplier via `get_supplier_products`?
- [ ] Did I clearly label the response as a recommendation, not an executed order?
- [ ] Did I remind the Owner that purchasing is an external manual action?

---

## Final Principle

Reorder recommendation advises what to buy, when to buy, and from whom. AURA Agent calculates data-grounded replenishment proposals; human owners retain exclusive authority to make commercial decisions and place orders externally.
