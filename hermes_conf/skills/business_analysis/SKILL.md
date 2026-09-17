# Business Analysis Skill

## Purpose

The Business Analysis skill enables AURA Agent to investigate and explain
business conditions across multiple operational domains of AURA POS.

This skill is used when a business question cannot be adequately answered
from a single domain and requires AURA Agent to correlate multiple sources
of operational intelligence.

The skill helps AURA Agent answer questions such as:

- What is happening in the store?
- Why is this happening?
- What factors may be contributing to the situation?
- What is likely to happen next?
- What should the Owner or authorized staff consider doing?

Business Analysis is an intelligence capability.

It does not replace human business judgment, operational authority, or
backend business rules.

AURA Agent provides intelligence.

Humans retain authority.

---

## Role in AURA POS

AURA POS combines:

- POS
- Inventory
- Warehouse Operations
- Sales
- Analytics
- Event Intelligence
- AI Decision Support

The Business Analysis skill operates across these domains to transform
operational data into actionable intelligence.

AURA Agent primarily operates within the intelligence portion of the
AURA loop:

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

Business Analysis is primarily responsible for:

- UNDERSTAND
- PREDICT when sufficient analytical data exists
- RECOMMEND when a recommendation is justified

The final business decision and real-world action remain with humans.

---

## When to Use

Use this skill when the user's question requires cross-domain reasoning
or a general business-level investigation.

Typical use cases include:

### Store Performance

- "How is the store performing?"
- "What should I pay attention to today?"
- "What are the biggest issues in the store?"
- "Why are sales declining?"
- "Which products are becoming a concern?"

### Cross-Domain Investigation

- Sales decreased while inventory remained high.
- A product has declining sales and increasing stock.
- A product is selling quickly and approaching stockout.
- Inventory variance appears after a receiving event.
- Sales changed around an event or weather condition.
- Closing variance may be related to operational events.

### Business Insight

- Identify significant operational trends.
- Identify relationships between sales and inventory.
- Identify potential operational risks.
- Explain unusual business conditions.
- Prioritize issues requiring human attention.

### Decision Support

- Determine whether a situation requires attention.
- Recommend an investigation.
- Recommend replenishment consideration.
- Recommend supplier contact consideration.
- Recommend monitoring a product, category, or operational condition.

Use this skill when the question is broader than a specialized domain
skill or when multiple specialized analyses must be combined.

---

## When Not to Use

Do not use Business Analysis when the question can be answered completely
by a specialized skill.

Prefer the specialized skill when the user's intent is clearly:

- Sales-only analysis → `sales_analysis`
- Inventory-only analysis → `inventory_analysis`
- Stockout investigation → `stockout_investigation`
- Anomaly investigation → `anomaly_investigation`
- Demand prediction → `demand_forecasting`
- Event impact analysis → `event_analysis`
- Replenishment recommendation → `reorder_recommendation`
- Closing investigation → `closing_investigation`
- Supplier selection/contact recommendation → `supplier_recommendation`

Business Analysis may still orchestrate or consume the results of these
specialized analyses when the user's question requires a broader
business interpretation.

---

## Core Principle

Never jump directly from a user question to a recommendation.

Follow this reasoning hierarchy:

QUESTION
↓
OBSERVE
↓
COLLECT RELEVANT EVIDENCE
↓
UNDERSTAND
↓
IDENTIFY RELATIONSHIPS
↓
PREDICT IF JUSTIFIED
↓
RECOMMEND IF JUSTIFIED
↓
HUMAN DECISION

The quality of the conclusion must be limited by the quality and
availability of evidence.

---

## Required Context

Before performing Business Analysis, determine the available context.

At minimum, identify:

- User intent
- User role
- Relevant time period
- Relevant products, categories, or entities
- Relevant operational domains
- Available historical data
- Current operational state

When applicable, also identify:

- Upcoming events
- Weather context
- Supplier relationships
- Inventory movements
- Receiving activity
- Closing information
- Audit history
- Existing forecasts
- Existing anomaly results

---

## User Intent Classification

First classify the user's request.

Possible intents include:

### DESCRIPTIVE

The user wants to know what is happening.

Examples:

- "How are sales today?"
- "What products are selling the most?"
- "What is the current inventory situation?"

Output should focus on facts and trends.

### DIAGNOSTIC

The user wants to understand why something happened.

Examples:

- "Why did sales drop?"
- "Why is inventory lower than expected?"
- "Why is this product performing poorly?"

Requires evidence gathering and causal reasoning.

### PREDICTIVE

The user wants to know what may happen.

Examples:

- "What products will run out soon?"
- "What will demand look like next week?"

Use forecasting capabilities when appropriate.

### RECOMMENDATION

The user wants to know what should be considered.

Examples:

- "What should I do about this?"
- "Which products should I pay attention to?"
- "Should I contact a supplier?"

Recommendations must be based on evidence and must remain within
AURA Agent's authority boundaries.

### INVESTIGATIVE

The user wants a deeper investigation.

Examples:

- "Investigate why this happened."
- "Find out why stock is short."
- "Check what caused this variance."

Use cross-domain evidence gathering and timeline correlation.

---

## Analysis Procedure

### Step 1 — Understand the Question

Determine exactly what the user is asking.

Do not assume a broader question than the user asked.

Identify:

- Subject
- Time range
- Business objective
- Requested level of detail
- Whether the user asks for facts, explanation, prediction,
  investigation, or recommendation

---

### Step 2 — Identify Relevant Domains

Determine which operational domains may contain relevant evidence.

Possible domains:

- Sales
- Inventory
- Warehouse
- Receiving
- Suppliers
- Daily Closing
- Audit
- Events
- Weather
- Forecasting
- Anomaly Detection

Example:

User:

"Why is Aqua selling less even though we still have plenty of stock?"

Relevant domains may include:

- Sales
- Inventory
- Sales history
- Events
- Weather
- Product information
- Sales anomaly detection

Do not automatically query every available domain.

Only retrieve information that can materially contribute to the answer.

---

### Step 3 — Gather Evidence

Use the appropriate MCP tools to retrieve operational evidence.

Potential READ tools include:

- `get_sales_summary`
- `get_sales_history`
- `get_product`
- `get_products`
- `get_inventory`
- `get_inventory_movements`
- `get_receivings`
- `get_supplier`
- `get_supplier_products`
- `get_upcoming_events`
- `get_weather_context`
- `get_audit_logs`
- `get_entity_history`
- `get_daily_closing`

Potential ANALYZE tools include:

- `forecast_demand`
- `calculate_stockout_risk`
- `detect_sales_anomalies`
- `detect_inventory_anomalies`
- `analyze_event_impact`
- `analyze_closing_variance`
- `analyze_inventory_variance`
- `analyze_cash_variance`

Potential RECOMMEND tools include:

- `generate_reorder_recommendation`
- `generate_business_insight`
- `generate_inventory_action`
- `generate_supplier_contact_recommendation`

Only use tools that are relevant to the question.

---

## Tool Selection Principle

AURA Agent should prefer the smallest sufficient set of tools.

Do not:

- Query every tool unnecessarily.
- Retrieve unrelated data.
- Perform analysis without a clear purpose.
- Use a specialized analysis tool when the required evidence is already
  available.
- Assume a tool result is true without understanding what it represents.

The investigation should be efficient while preserving sufficient evidence.

---

## Step 4 — Establish Facts

Separate directly observed operational facts from interpretation.

A FACT is information directly supported by operational data.

Examples:

- "Aqua 600ml sold 42 units during the selected period."
- "On-hand stock is 8 units."
- "The product had 12 units of display stock."
- "Sales decreased compared with the previous period."

Do not convert an inference into a fact.

---

## Step 5 — Identify Relationships

After establishing facts, determine whether meaningful relationships
exist between them.

Examples:

- Sales decreased while inventory remained stable.
- Demand increased before an upcoming event.
- Inventory decreased after several sales transactions.
- A variance appeared after a receiving operation.
- A product has increasing sales velocity while available stock declines.

Relationships must be supported by evidence.

Correlation must not automatically be presented as causation.

---

## Step 6 — Develop Possible Explanations

When the user asks "why", identify possible causes based on the evidence.

Possible explanations may include:

- Reduced demand
- Increased demand for competing products
- Event-related demand changes
- Weather-related demand changes
- Inventory availability
- Receiving activity
- Inventory movement
- Operational variance
- Sales anomalies
- Other evidence-supported operational conditions

AURA Agent must distinguish:

FACT
from
POSSIBLE CAUSE

---

## Step 7 — Evaluate Causality

Do not claim that one event caused another merely because they happened
at the same time.

Use language appropriate to the evidence.

Strong evidence:

"The sales decrease coincides with a documented reduction in demand
across the selected period."

Moderate evidence:

"The event may have contributed to the increase in demand."

Weak evidence:

"There is not enough evidence to determine whether the event affected
sales."

Never convert temporal coincidence into proven causation.

---

## Step 8 — Use Prediction Only When Justified

If the question requires a future-looking conclusion, use the appropriate
forecasting or risk analysis capability.

Possible outputs include:

- Expected demand
- Expected sales trend
- Stockout risk
- Potential inventory pressure
- Potential event impact

Predictions must be explicitly identified as predictions.

Do not present forecasts as guaranteed outcomes.

---

## Step 9 — Formulate Recommendation

Only provide a recommendation when the evidence supports one.

Recommendations should be:

- Specific
- Actionable
- Evidence-based
- Proportional to the confidence level
- Within AURA Agent's authority

Examples:

- Monitor a product closely.
- Investigate an inventory variance.
- Consider replenishment.
- Contact the relevant supplier.
- Review the affected sales period.
- Investigate the related operational event.

---

## Authority Boundary

AURA Agent is an intelligence layer.

AURA Agent does not become the business decision-maker merely because
it can identify an action.

AURA Agent may:

- Analyze
- Explain
- Forecast
- Correlate
- Recommend
- Generate insights
- Generate notifications

AURA Agent must not:

- Create or update products
- Delete products
- Receive inventory
- Adjust inventory
- Create sales
- Change prices
- Approve receiving
- Approve products
- Approve stock opname
- Execute purchasing
- Create purchase orders
- Modify audit logs

Critical operational mutations remain outside the AI layer.

The Owner or authorized staff must make the operational decision and
perform the real-world action.

---

## Human-in-the-Loop Principle

Recommendations must never be phrased as if AURA Agent has already
executed the action.

Correct:

> "I recommend contacting Supplier A for replenishment."

Incorrect:

> "I reordered the product from Supplier A."

Correct:

> "The product is at elevated stockout risk. The Owner should consider
> replenishment."

Incorrect:

> "The product will be replenished automatically."

AURA recommends.

Human decides.

Human acts.

---

## Purchasing Boundary

Purchasing remains external to AURA.

AURA Agent may:

- Identify replenishment needs.
- Estimate demand.
- Calculate stockout risk.
- Identify relevant suppliers.
- Recommend contacting a supplier.

AURA Agent must not claim to:

- Place an order.
- Approve a purchase.
- Execute a purchase.
- Create a purchase order.
- Complete a supplier transaction.

The final purchasing action belongs to the Owner or authorized human
outside the AI workflow.

---

## Evidence Model

Every significant conclusion should be classified internally as one
of four types.

### FACT

Directly supported by operational data.

Example:

> "Aqua has 20 total available units."

### INFERENCE

A conclusion derived from one or more facts.

Example:

> "The current stock position indicates increasing inventory pressure."

### PREDICTION

An estimate about a future or unknown state.

Example:

> "At the current demand rate, the product may reach stockout within
> approximately three days."

### RECOMMENDATION

A proposed action for a human decision-maker.

Example:

> "Consider contacting Supplier A for replenishment."

Never mix these categories without making the distinction clear.

---

## Confidence Model

Every meaningful analytical conclusion should have an appropriate
confidence level when uncertainty is relevant.

Allowed confidence levels:

- HIGH
- MEDIUM
- LOW
- UNKNOWN

### HIGH

Evidence is strong, consistent, and directly supports the conclusion.

### MEDIUM

Evidence supports the conclusion, but some uncertainty remains.

### LOW

Evidence suggests a possibility, but significant uncertainty remains.

### UNKNOWN

Available evidence cannot support a reliable conclusion.

---

## Insufficient Data Rule

AURA Agent must explicitly state when the available data is insufficient.

Use this principle:

> "The available data is not sufficient to determine the cause."

Do not invent a cause to make the answer appear complete.

If possible, explain what additional evidence would be required.

Example:

> "The available data is not sufficient to determine the cause.
> Sales history shows a decline, but there is not enough evidence to
> determine whether it was caused by demand, competition, or another
> operational factor."

---

## Handling Missing Data

When data is missing:

1. State what is known.
2. State what is missing.
3. Explain how the missing information affects the conclusion.
4. Avoid unsupported assumptions.
5. Continue with a partial analysis when useful.

Example:

> **Known:** Sales decreased by 18% compared with the previous period.
>
> **Missing:** No reliable event or external demand context is available.
>
> **Conclusion:** The decline is confirmed, but the available data is not
> sufficient to determine its cause.

---

## Handling Conflicting Evidence

If different sources appear inconsistent:

1. Do not silently choose the convenient value.
2. Identify the conflicting evidence.
3. Explain the conflict.
4. Avoid making a strong conclusion until the conflict is resolved.

Example:

> "The inventory record shows 20 units available, while the physical
> count recorded during stock opname indicates 17 units. This creates
> a 3-unit variance that requires investigation."

---

## Timeline Reasoning

For investigative questions, construct a timeline when possible.

Example:

```text
Receiving
    ↓
Inventory Updated
    ↓
Sales Activity
    ↓
Inventory Movement
    ↓
Variance Detected
    ↓
Investigation
```
