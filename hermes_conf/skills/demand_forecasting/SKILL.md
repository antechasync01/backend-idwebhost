# Demand Forecasting Skill

## Purpose

The Demand Forecasting skill enables AURA Agent to estimate future product demand and sales velocity over defined planning horizons. It combines historical sales baselines with calendar events, weather context, and category trends.

Questions answered:
- How many units of Product X will we sell over the next 7 or 14 days?
- What is projected demand for beverages during this weekend's heatwave?
- How will upcoming public holidays or payday cycles impact staple foods?
- Which products should anticipate rising demand in the coming week?

This skill produces probabilistic forward projections. It does not guarantee sales outcomes or execute purchase orders.

---

## When to Use

Use when the user requests forward-looking demand estimates or sales volume projections:

### Horizon Demand Estimates
- "What is the expected demand for Aqua 600ml over the next 7 days?"
- "How much Indomie Goreng will we likely sell in the next two weeks?"
- "Forecast daily sales rate for fresh milk this week."

### Context-Driven Demand Projections
- "Will the upcoming long weekend increase snack and beverage sales?"
- "Forecast cooking oil demand leading up to Ramadan."
- "How will forecasted heavy rain affect overall store foot traffic and instant noodle demand?"

### Replenishment Input
- Supplying forward demand rates to `stockout_investigation` or `reorder_recommendation`.

---

## When Not to Use

Route questions that do not focus on forward-looking demand prediction:
- Reviewing historical sales performance or past period comparisons → `sales_analysis`
- Evaluating current inventory runout days with existing stock → `stockout_investigation`
- Calculating exact purchase quantities and supplier selection → `reorder_recommendation`
- Analyzing historical event impact without forward projection → `event_analysis`
- Investigating sudden sales drops or anomalies → `anomaly_investigation`

---

## Required Context

Identify before generating forecasts:
- Target Entity: Product, category, or store-level scope
- Forecast Horizon: 3 days, 7 days, 14 days, or 30 days
- Historical Baseline: 14-day or 30-day moving sales average
- Context Signals: Upcoming holidays, payday periods, weather forecasts, local events

---

## MCP Tools

Use only authorized PRD tools:

### READ Tools
- `get_sales_history`: Retrieve historical transaction velocity and day-of-week patterns.
- `get_product` / `get_products`: Retrieve product catalog data and category baselines.
- `get_upcoming_events`: Identify upcoming holidays, festivals, and community events.
- `get_weather_context`: Check multi-day weather outlooks (e.g., heavy rain, heatwave).

### ANALYZE Tools
- `forecast_demand`: Compute forward demand rates, expected units, and confidence intervals.
- `analyze_event_impact`: Extract demand multipliers from past similar events.

### RECOMMEND Tools
- `generate_business_insight`: Synthesize demand shift patterns into owner-level summaries.

---

## Reasoning Procedure

1. **Define Horizon & Scope**: Specify the product/category and the target forward window (e.g., next 7 days).
2. **Establish Historical Baseline**: Query `get_sales_history` over a stable period (minimum 14–30 days) to compute Average Daily Sales (ADS):
```text
Baseline Daily Demand = Total Historical Units Sold / Number of Operating Days
```
3. **Incorporate Day-of-Week Patterns**: Adjust for weekend versus weekday variations (e.g., weekend volume is historically 1.4x weekday volume).
4. **Apply Contextual Modifiers**:
   - Query `get_upcoming_events` for holidays, paydays, or local gatherings.
   - Query `get_weather_context` for weather forecasts that affect foot traffic or specific categories.
   - Call `analyze_event_impact` if historical event precedents exist.
5. **Execute Forecast Calculation**: Call `forecast_demand` to generate baseline projection and prediction intervals (lower bound, expected, upper bound).
6. **Separate Observation from Prediction**: Explicitly label past sales as historical facts and forward estimates as probabilistic projections.
7. **Assign Confidence**: Calibrate confidence based on historical data volume and external signal clarity.

---

## Evidence Requirements

| Finding Component | Required MCP Evidence |
| :--- | :--- |
| Historical Baseline | `get_sales_history` spanning at least 14 days |
| Forward Projection | `forecast_demand` calculated output |
| Event Adjustment | `get_upcoming_events` matched with `analyze_event_impact` precedent |
| Weather Multiplier | `get_weather_context` confirmed forecast |

Core Rule:
A historical sales rate is an observation, not a guarantee of future behavior. All outputs are PREDICTIONS, never FACTS.

When data is insufficient to project forward demand:
> "Available historical data is insufficient to produce a reliable demand forecast."

---

## Uncertainty Handling

- **Short History (< 14 days)**: Note that the forecast has high variance; report wide prediction intervals and set confidence to LOW.
- **Unprecedented Events**: When an upcoming event has no historical match in AURA POS, state the baseline forecast and declare the event multiplier unquantified.
- **Stockout Distortions**: If the product was previously stocked out during the baseline period, historical sales undercount true demand. Adjust baseline or state the limitation.

---

## Output Format

```markdown
## Forecast Summary
[Concise summary of projected demand over the requested horizon]

## Historical Baseline
- Observation Window: [e.g., Past 14 days]
- Average Daily Sales (ADS): [N] units/day
- Weekend Multiplier: [e.g., +30% vs weekdays]

## Context Modifiers
- Calendar / Events: [Upcoming holiday or payday impact]
- Weather Forecast: [Expected weather signal and category impact]

## Demand Projection
- Target Horizon: [e.g., Next 7 Days (2026-09-15 to 2026-09-21)]
- Expected Total Demand: [E] units (Range: [Min] – [Max] units)
- Projected Daily Burn Rate: [D] units/day

## Confidence
[HIGH | MEDIUM | LOW | UNKNOWN] — [Brief justification]

## Planning Insight
[Operational takeaways for inventory replenishment or display preparation]
```

---

## Examples

### Example 1: Standard 7-Day Baseline Forecast

```markdown
## Forecast Summary
Aqua 600ml is projected to sell approximately 98 units over the next 7 days (14 units/day).

## Historical Baseline
- Observation Window: Past 21 days (`get_sales_history`)
- Average Daily Sales (ADS): 13.8 units/day
- Weekend Pattern: Saturday and Sunday average 17.5 units/day; weekdays average 12.3 units/day.

## Context Modifiers
- Calendar / Events: No major public holidays scheduled (`get_upcoming_events`).
- Weather Forecast: Normal clear weather expected (`get_weather_context`).

## Demand Projection
- Target Horizon: Next 7 Days (2026-09-13 to 2026-09-19)
- Expected Total Demand: 98 units (Range: 88 – 108 units)
- Projected Daily Burn Rate: ~14.0 units/day

## Confidence
HIGH — Stable 21-day sales history with consistent day-of-week seasonality.

## Planning Insight
Current inventory should be checked via `stockout_investigation` to ensure total available stock covers the 98-unit projected demand.
```

### Example 2: Weather & Event Adjusted Forecast

```markdown
## Forecast Summary
Pocari Sweat 500ml is projected to experience elevated demand of 65 units this weekend due to hot weather and a local fun run.

## Historical Baseline
- Observation Window: Past 30 days
- Standard Weekend Demand: 36 units (18 units/day)

## Context Modifiers
- Calendar / Events: "Kecamatan Fun Run" passes within 200m of store on Sunday (`get_upcoming_events`). Past event impact: +45% beverage lift (`analyze_event_impact`).
- Weather Forecast: High temperatures (34°C) forecast for Saturday and Sunday (`get_weather_context`).

## Demand Projection
- Target Horizon: Weekend (2026-09-19 to 2026-09-20)
- Expected Total Demand: 65 units (Range: 55 – 75 units)
- Projected Weekend Burn Rate: ~32.5 units/day

## Confidence
MEDIUM — Clear weather and event triggers exist, but exact runner foot traffic carries uncertainty.

## Planning Insight
Store should prepare adequate chilled display stock by Friday afternoon.
```

---

## What This Skill Must Never Do

- Never represent forecasts as guaranteed facts or commitments.
- Never execute purchase orders or supplier orders.
- Never invent historical averages or baseline metrics without data.
- Never ignore past stockout periods that artificially depressed historical sales.
- Never bypass the MCP gateway to query PostgreSQL directly.

---

## Relationship With Other Skills

```text
               demand_forecasting
                       │
      ┌────────────────┼────────────────┐
      ▼                ▼                ▼
event_analysis   stockout_investigation reorder_recommendation
(Quantifies event (Calculates runout     (Calculates purchase
 demand multipliers) risk against stock) quantity to restock)
```

- `event_analysis`: Supplies historical impact percentages for upcoming events.
- `stockout_investigation`: Uses forecast burn rate to evaluate runout days.
- `reorder_recommendation`: Uses total horizon demand to compute optimal order size.

---

## Reasoning Checklist

- [ ] Did I establish a baseline from actual historical sales?
- [ ] Did I check day-of-week patterns (weekday vs weekend)?
- [ ] Did I review upcoming calendar events and weather forecasts?
- [ ] Did I present demand as a projection with a range rather than a certainty?
- [ ] Did I account for past stockouts that might have suppressed baseline sales?
- [ ] Did I avoid claiming to place orders or restock shelves?

---

## Final Principle

Demand forecasting estimates forward operational probability, never certainty. AURA Agent calculates data-grounded projections with transparent confidence bounds; human managers retain full responsibility for purchasing and merchandising decisions.
