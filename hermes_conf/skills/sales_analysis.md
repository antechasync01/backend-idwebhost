# Sales Analysis Skill

## Purpose

The Sales Analysis skill enables AURA Agent to analyze sales performance
and sales-related behavior using operational sales data from AURA POS.

Its purpose is to transform raw sales information into understandable
sales intelligence.

This skill helps AURA Agent answer questions such as:

- What is selling?
- What is not selling?
- How are sales changing?
- Which products contribute most to sales?
- Which products are declining?
- Which products are growing?
- How does the current period compare with another period?
- Is a sales change significant enough to investigate?
- Are there indications of unusual sales behavior?

This skill focuses on understanding sales.

It does not own forecasting, inventory investigation, event analysis,
or purchasing decisions.

Those responsibilities belong to their respective skills.

---

## Role in AURA POS

Sales Analysis operates within the intelligence layer of AURA POS.

The general intelligence flow is:

OBSERVE
↓
UNDERSTAND
↓
PREDICT
↓
RECOMMEND
↓
HUMAN DECISION
↓
REAL-WORLD ACTION

Sales Analysis primarily supports:

- OBSERVE
- UNDERSTAND

It may provide evidence for:

- Demand Forecasting
- Event Analysis
- Stockout Investigation
- Anomaly Investigation
- Business Analysis
- Reorder Recommendation

Sales Analysis does not independently execute business actions.

---

## When to Use

Use this skill when the primary subject of the user's question is
sales performance or sales behavior.

Typical use cases include:

### Sales Performance

- "How are sales today?"
- "How were sales this week?"
- "How much did we sell yesterday?"
- "What are our best-selling products?"
- "Which products generated the most sales?"

### Sales Trends

- "Are sales increasing?"
- "Are sales declining?"
- "What is the sales trend this month?"
- "Which products are growing?"
- "Which products are declining?"

### Period Comparison

- "Compare this week with last week."
- "Compare today's sales with yesterday."
- "How does this month compare with last month?"
- "Which products changed the most?"

### Product Performance

- "What are the top-selling products?"
- "Which products have poor sales?"
- "Which product contributes the most units sold?"
- "Which products are losing momentum?"

### Sales Investigation

- "Why did sales drop?"
- "Why is this product selling less?"
- "Why did sales suddenly increase?"
- "Is this sales change unusual?"

When the question requires additional domains to explain the cause,
Sales Analysis should provide the sales evidence and defer the broader
investigation to the appropriate specialized skill.

---

## When Not to Use

Do not use this skill as the primary skill when the user's intent is
clearly about:

- Inventory state → `inventory_analysis`
- Stockout risk → `stockout_investigation`
- Future demand → `demand_forecasting`
- Event impact → `event_analysis`
- General cross-domain business analysis → `business_analysis`
- Inventory or sales anomaly investigation → `anomaly_investigation`
- Closing variance → `closing_investigation`
- Replenishment → `reorder_recommendation`
- Supplier selection/contact → `supplier_recommendation`

Sales Analysis may provide supporting evidence to these skills when
sales data is relevant.

---

## Required Context

Before analyzing sales, determine:

- Sales subject
- Relevant time period
- Comparison period, if applicable
- Product or category scope
- Requested metric
- User intent

Possible sales metrics include:

- Total sales
- Number of transactions
- Units sold
- Product sales
- Category sales
- Sales growth
- Sales decline
- Average sales
- Sales velocity
- Sales distribution
- Sales frequency

Only use metrics that are actually available from the MCP response.

---

## Time Period Handling

Always establish the time period before interpreting sales.

Examples:

- Today
- Yesterday
- This week
- Last week
- This month
- Last month
- Custom date range

When comparing periods, ensure that the comparison is meaningful.

Prefer comparable periods such as:

```text
This week
    vs
Previous week
```
