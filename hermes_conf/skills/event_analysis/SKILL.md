# Event Analysis Skill

## Purpose

The Event Analysis skill enables AURA Agent to evaluate how external and calendar events—such as holidays, weather conditions, payday cycles, and local festivals—influence store foot traffic, category sales, and product demand.

Questions answered:
- Did the holiday weekend increase snack and beverage sales?
- How did heavy rainfall affect store foot traffic and instant food sales?
- What was the sales uplift during the local fun run?
- Which categories benefit most from monthly payday cycles?
- How have past similar events influenced store performance?

This skill analyzes correlations between external contexts and store performance. It does not alter prices, schedule promotions, or execute reorders.

---

## When to Use

Use when evaluating the operational impact of external contexts or weather:

### Retrospective Impact
- "How did the Independence Day holiday affect store sales?"
- "Did yesterday's storm reduce foot traffic or increase instant noodle sales?"
- "What was the sales uplift during the neighborhood tournament?"

### Category Sensitivity
- "Which categories are most sensitive to rainy weather?"
- "How much do bottled water sales increase during hot weekends?"
- "What is the typical sales lift during payday (25th–28th)?"

### Planning Input
- Supplying category uplift factors to `demand_forecasting` for upcoming events.

---

## When Not to Use

Route inquiries that do not center on external context:
- General store or product sales performance → `sales_analysis`
- Quantitative forward demand projections → `demand_forecasting`
- Investigating depleted stock or runout risk caused by events → `stockout_investigation`
- Identifying internal inventory shrinkage → `anomaly_investigation`
- Calculating purchase quantities for upcoming events → `reorder_recommendation`

---

## Required Context

Identify before analyzing:
- Event Identity: Holiday, weather condition, payday cycle, or community event
- Event Timeline: Specific event dates and operating hours
- Comparison Baseline: Equivalent non-event period (e.g., preceding week)
- Target Scope: Store-wide totals, specific categories, or SKUs
- Weather Context: Temperature, precipitation level, or alerts

---

## MCP Tools

Use only PRD-defined tools:

### READ Tools
- `get_upcoming_events`: Identify scheduled holidays, paydays, and local events.
- `get_weather_context`: Retrieve historic weather records and forecasts.
- `get_sales_history`: Analyze transaction logs, velocity, and product sales.
- `get_sales_summary`: Retrieve period totals, transaction counts, and basket sizes.
- `get_product` / `get_products`: Access category classifications and catalog metadata.

### ANALYZE Tools
- `analyze_event_impact`: Compute statistical sales uplift/downlift against baselines.
- `forecast_demand`: Project forward demand when event impact informs future planning.

### RECOMMEND Tools
- `generate_business_insight`: Document reusable event patterns for Owner review.

---

## Reasoning Procedure

1. **Establish Window & Baseline**: Define event dates and select a comparable non-event baseline (e.g., event weekend vs preceding normal weekend).
2. **Collect Environmental Signals**:
   - Query `get_upcoming_events` for event type and schedule.
   - Query `get_weather_context` for temperature or rainfall records.
3. **Retrieve Sales Metrics**:
   - Query `get_sales_summary` for revenue, ticket count, and basket size.
   - Query `get_sales_history` for category and product volume shifts.
4. **Calculate Operational Impact**: Call `analyze_event_impact` to compute:
```text
Event Impact (%) = ((Event Metric - Baseline Metric) / Baseline Metric) * 100
```
5. **Evaluate Correlation vs Causation**:
   - Verify whether sales changes coincided directly with event timing.
   - Check confounding factors (stockouts, concurrent discounts).
   - Label relationships as *associated with* rather than proven direct causation.
6. **Assign Confidence**: Calibrate based on baseline comparability and data quality.

---

## Evidence Requirements

| Finding Component | Required MCP Evidence |
| :--- | :--- |
| Event Occurrence | `get_upcoming_events` or calendar record |
| Weather Condition | `get_weather_context` precipitation/temperature record |
| Sales Variance | `get_sales_summary` comparison between event and baseline |
| Category Uplift | `analyze_event_impact` statistical difference > 10% |

Causality Rule:
Temporal coincidence does not establish proven causation. Sales increases during an event are associations, not definitive proof of sole cause.

If available data cannot confirm the relationship:
> "Cause could not be determined from available data."

---

## Uncertainty Handling

- **Simultaneous Events**: When multiple factors occur together (e.g., rain on payday), note that individual effects cannot be cleanly isolated.
- **Unregistered Events**: If an event is absent from `get_upcoming_events`, note the absence of official records and analyze available sales data provisionally.
- **Stockout Distortions**: If top-selling items ran out of stock during the event, note that recorded sales underestimate true demand.

---

## Output Format

```markdown
## Event Summary
[Concise description of the event and overall impact on store sales]

## Event Profile
- Event Name: [Name / Description]
- Dates Observed: [YYYY-MM-DD to YYYY-MM-DD]
- Context Type: [Holiday | Weather | Payday | Community Event]
- Environmental Context: [Weather, temperature, foot traffic notes]

## Baseline Comparison
- Baseline Period: [Reference dates] (Revenue: [Rp X], Transactions: [Y])
- Event Period: [Observed dates] (Revenue: [Rp A], Transactions: [B])
- Net Change: [+/- X%] in Revenue, [+/- Y%] in Transactions

## Category & Product Impact
- High-Impact Categories: [Category Name: +X% uplift]
- Top Contributing Products: [Product Name: Units Sold vs Baseline]
- Suppressed Categories: [Category Name: -X% decline]

## Analysis & Causality
[Evidence-based explanation of operational relationships and confounding factors]

## Confidence
[HIGH | MEDIUM | LOW | UNKNOWN] — [Brief justification]

## Operational Takeaways
[Practical insights for future stock preparation or merchandising]
```

---

## Examples

### Example 1: Holiday Weekend Impact on Beverages and Snacks

```markdown
## Event Summary
The Independence Day weekend (2026-08-15 to 2026-08-17) produced a +28.4% revenue increase, led by packaged beverages and snacks.

## Event Profile
- Event Name: Independence Day Long Weekend
- Dates Observed: 2026-08-15 to 2026-08-17 (3 days)
- Context Type: Public Holiday / Long Weekend
- Environmental Context: Clear, sunny weather (31°C–33°C) (`get_weather_context`)

## Baseline Comparison
- Baseline Period: Previous weekend (2026-08-08 to 2026-08-10)
- Baseline Metrics: Rp 14,200,000 across 342 transactions
- Event Metrics: Rp 18,230,000 across 418 transactions
- Net Change: +28.4% Revenue, +22.2% Transactions

## Category & Product Impact
- Ready-to-Drink Beverages: +42.0% uplift (Aqua 600ml: 124 vs 78 units baseline)
- Snacks & Chips: +35.5% uplift (Chitato 68g: 52 vs 34 units baseline)

## Analysis & Causality
Uplift coincided with neighborhood celebrations and warm weather. Beverage demand peaked between 14:00 and 17:00 daily.

## Confidence
HIGH — Clear baseline comparability and consistent category uplift across 3 days.

## Operational Takeaways
Increase display stock of cold drinks and family snacks by 35% before national holiday weekends.
```

### Example 2: Heavy Rain Impact on Foot Traffic and Instant Foods

```markdown
## Event Summary
Torrential rain on 2026-09-08 reduced store transactions by 18%, but triggered a +32% surge in instant noodle purchases.

## Event Profile
- Event Name: Monsoon Rainfall
- Dates Observed: 2026-09-08 (11:00–21:00)
- Context Type: Weather Event
- Environmental Context: Heavy precipitation (74mm rainfall) (`get_weather_context`)

## Baseline Comparison
- Baseline Period: Preceding Tuesday (2026-09-01)
- Baseline Metrics: Rp 4,800,000 across 115 transactions
- Event Metrics: Rp 3,950,000 across 94 transactions
- Net Change: -17.7% Revenue, -18.3% Transactions

## Category & Product Impact
- Instant Noodles: +32.4% uplift (Indomie Soto: 48 vs 31 units baseline)
- Hot Beverages: +25.0% uplift (Torabika Duo: 30 vs 21 units baseline)
- Cold Beverages: -45.0% decline

## Analysis & Causality
Rain discouraged foot traffic, reducing total transactions. However, visiting shoppers purchased larger baskets centered on warm meals.

## Confidence
HIGH — Directly confirmed by transaction count drop and contrasting category shifts.

## Operational Takeaways
During forecasted rainy days, position instant noodles and coffee sachets near the entrance.
```

---

## What This Skill Must Never Do

- Never assert causation purely because sales moved during an event.
- Never invent event schedules, weather readings, or attendance numbers.
- Never modify product prices, apply discounts, or schedule promotions.
- Never trigger purchase orders or supplier contracts.
- Never bypass the MCP gateway to access PostgreSQL directly.

---

## Relationship With Other Skills

```text
               event_analysis
                     │
     ┌───────────────┼───────────────┐
     ▼               ▼               ▼
sales_analysis  demand_forecasting  stockout_investigation
(Supplies past  (Consumes event     (Checks if event surge
 sales numbers)  multipliers)        caused stockout)
```

- `sales_analysis`: Supplies sales summaries and transaction details for baselines.
- `demand_forecasting`: Uses event uplift percentages to adjust future projections.
- `stockout_investigation`: Consults event analysis to verify if event surge caused stockout.

---

## Reasoning Checklist

- [ ] Did I choose a meaningful, comparable non-event baseline?
- [ ] Did I retrieve verified event and weather records via MCP tools?
- [ ] Did I distinguish total store movement from category-specific movement?
- [ ] Did I distinguish correlation from proven causation?
- [ ] Did I check confounding factors like stockouts or promotions?
- [ ] Did I state the limitation phrase if causality cannot be proven?
- [ ] Did I avoid proposing price changes or automatic promotions?

---

## Final Principle

Event analysis explains the intersection of store performance and external reality. AURA Agent measures operational associations with analytical rigor, providing actionable lessons while leaving business actions to human operators.
