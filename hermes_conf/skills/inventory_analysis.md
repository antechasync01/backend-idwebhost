# Inventory Analysis Skill

## Purpose

The Inventory Analysis skill enables AURA Agent to understand, analyze,
and explain the current and historical inventory condition of AURA POS.

Its purpose is to transform inventory data into operational intelligence.

This skill helps AURA Agent answer questions such as:

- How much stock do we currently have?
- Which products have low stock?
- Which products have high stock?
- How is inventory changing?
- Why is inventory changing?
- Which products require attention?
- What inventory movements occurred?
- Is the current inventory position unusual?
- Is there a difference between expected and actual inventory?

This skill focuses on understanding inventory conditions.

It does not independently execute inventory mutations, approve stock
adjustments, perform receiving, or make purchasing decisions.

---

## Role in AURA POS

Inventory is one of the core operational domains of AURA POS.

The inventory model uses:

```text
Display Stock
+
On-Hand Stock
=
Total Available
```

Total Available is derived from Display Stock and On-Hand Stock.

Inventory Analysis must always respect this model.

The inventory source of truth is the operational inventory state maintained
by the backend.

AURA Agent must not create an alternative inventory state.

---

## Core Inventory Model

### Display Stock

Display Stock represents inventory currently available in the store
display area.

### On-Hand Stock

On-Hand Stock represents inventory physically held outside the display
area, such as warehouse stock.

### Total Available

Total Available represents the combined available stock.

```text
Total Available = Display Stock + On-Hand Stock
```

AURA Agent must not treat Total Available as an independently maintained
quantity when analyzing inventory.

Example:

```text
Display Stock = 12
On-Hand Stock = 8

Total Available = 20
```

---

## When to Use

Use this skill when the primary subject of the user's question is
inventory.

Typical use cases include:

### Current Inventory

- "How much Aqua do we have?"
- "Which products are low in stock?"
- "How much stock is in the warehouse?"
- "Which products have the most available stock?"

### Inventory Distribution

- "How much stock is on display?"
- "How much stock is in the warehouse?"
- "Which products have most of their stock in the warehouse?"
- "Which products have low display stock?"

### Inventory Changes

- "Why did this product's stock decrease?"
- "What happened to the inventory today?"
- "How has stock changed this week?"
- "What inventory movements occurred?"

### Inventory Investigation

- "Why is the stock different?"
- "Why is the inventory lower than expected?"
- "Is there an inventory problem?"
- "What caused this inventory change?"

### Inventory Monitoring

- "Which inventory should I pay attention to?"
- "Which products are running low?"
- "Which products have unusually high stock?"

When the question requires a deeper investigation into a specific variance,
use `stockout_investigation` or `anomaly_investigation` as appropriate.

---

## When Not to Use

Do not use Inventory Analysis as the primary skill when the user's intent
is clearly:

- Sales performance → `sales_analysis`
- Future demand → `demand_forecasting`
- Stockout investigation → `stockout_investigation`
- Anomaly investigation → `anomaly_investigation`
- Event impact → `event_analysis`
- Replenishment recommendation → `reorder_recommendation`
- Supplier recommendation → `supplier_recommendation`
- Closing variance → `closing_investigation`

Inventory Analysis may provide supporting inventory evidence to these
skills.

---

## Required Context

Before analyzing inventory, identify:

- Product or product scope
- Current or historical time period
- Inventory state being requested
- Whether the user wants current status, change, or explanation
- Whether a comparison is required

Potential inventory dimensions include:

- Display Stock
- On-Hand Stock
- Total Available
- Inventory movements
- Receiving
- Stock opname
- Expected inventory
- Historical inventory state

---

## MCP Tools

Primary READ tools:

- `get_inventory`
- `get_inventory_movements`

Supporting READ tools:

- `get_product`
- `get_products`
- `get_sales_history`
- `get_receivings`
- `get_daily_closing`
- `get_entity_history`
- `get_audit_logs`

Potential ANALYZE tools:

- `calculate_stockout_risk`
- `detect_inventory_anomalies`
- `analyze_inventory_variance`

Use only the tools necessary for the question.

---

## Tool Selection

### `get_inventory`

Use for:

- Current inventory
- Display stock
- On-hand stock
- Total available
- Product stock comparison

Example:

> "How much Aqua do we have?"

### `get_inventory_movements`

Use for:

- Inventory changes
- Stock movement history
- Movement timeline
- Investigating why stock changed

Example:

> "What happened to Aqua's stock today?"

### `get_sales_history`

Use when sales activity may explain inventory changes.

Example:

> "Why did Aqua stock decrease by 20 units?"

### `get_receivings`

Use when receiving activity may explain an inventory increase.

### `get_daily_closing`

Use when closing information is relevant to the inventory state.

### `get_entity_history`

Use when a broader historical timeline of an inventory entity is required.

### `get_audit_logs`

Use when an investigation requires audit evidence.

### `calculate_stockout_risk`

Use when the user asks about stockout risk or when inventory analysis
needs an explicit stockout-risk assessment.

For deeper stockout investigation, use:

`stockout_investigation`.

### `detect_inventory_anomalies`

Use when the inventory behavior appears unusual and anomaly detection
is appropriate.

### `analyze_inventory_variance`

Use when expected inventory and actual inventory need to be compared.

---

## Analysis Procedure

### Step 1 — Identify the Inventory Subject

Determine whether the question concerns:

- One product
- Multiple products
- A category
- Entire store inventory
- Display stock
- On-hand stock
- Total available
- Inventory movement

---

### Step 2 — Establish the Time Context

Determine whether the user asks about:

- Current state
- A specific date
- A historical period
- A change between two periods

Do not mix current inventory with historical inventory without explicitly
stating the difference.

---

### Step 3 — Retrieve Inventory Data

Retrieve the minimum sufficient data required to answer the question.

For a simple current-stock question:

- `get_inventory`

may be sufficient.

For an inventory-change question:

- `get_inventory`
- `get_inventory_movements`

may be required.

For a deeper investigation:

- `get_inventory`
- `get_inventory_movements`
- `get_sales_history`
- `get_receivings`
- `get_audit_logs`

may be appropriate.

---

### Step 4 — Establish Inventory Facts

Identify directly observed inventory facts.

Examples:

- "Display stock is 12 units."
- "On-hand stock is 8 units."
- "Total available stock is 20 units."
- "Inventory decreased by 5 units during the selected period."

Facts must be directly supported by operational data.

---

### Step 5 — Validate Inventory Arithmetic

When Display Stock and On-Hand Stock are available, verify:

```text
Total Available = Display Stock + On-Hand Stock
```

Example:

```text
Display = 12
On-Hand = 8
Total = 20
```

If the reported Total Available does not match the derived value,
do not silently replace the backend value.

Report the inconsistency and defer to the authoritative backend state
or appropriate investigation.

---

## Inventory State Interpretation

Inventory should be interpreted according to its operational state.

### Healthy

Inventory is available and there is no evidence of immediate operational
pressure.

Do not call inventory "healthy" solely because the quantity is large.

### Low

Inventory quantity is relatively low according to the available context.

"Low" should be contextual rather than based on an arbitrary threshold
invented by AURA Agent.

### High

Inventory quantity is relatively high compared with the relevant context.

High stock does not automatically mean overstock.

### Critical

Use only when the available operational data clearly indicates a
significant inventory risk.

Do not invent critical thresholds.

---

## Display Stock Analysis

Display Stock should be analyzed independently when relevant.

Example:

```text
Display Stock = 2
On-Hand Stock = 50
Total Available = 52
```

The store may have sufficient total inventory while the display itself
is nearly empty.

Therefore:

```text
Low Display Stock
       ≠
Low Total Available
```

AURA Agent must preserve this distinction.

---

## On-Hand Analysis

On-Hand Stock represents inventory outside the display area.

Example:

```text
Display = 5
On-Hand = 80
Total = 85
```

The product may have substantial inventory available in the warehouse
even though the display quantity is low.

Do not interpret low Display Stock as overall stock shortage without
checking On-Hand Stock.

---

## Total Available Analysis

Total Available should be interpreted as:

```text
Display + On-Hand
```

Example:

```text
Display = 10
On-Hand = 15

Total Available = 25
```

Do not double-count Display and On-Hand when presenting total inventory.

---

## Inventory Movement Analysis

Inventory movements should be analyzed as events affecting inventory.

Potential movement categories may include:

- Sale-related decrease
- Receiving-related increase
- Display transfer
- Stock opname
- Other authorized inventory events

AURA Agent must use the actual movement data returned by the backend
rather than assuming a movement occurred.

### Inventory Increase

When inventory increases, investigate relevant evidence such as:

- Receiving
- Inventory movement
- Transfer
- Stock opname
- Other operational events

Do not automatically assume:

> "The warehouse received new stock."

unless receiving evidence confirms it.

### Inventory Decrease

When inventory decreases, investigate relevant evidence such as:

- Sales
- Display transfer
- Inventory movements
- Stock opname
- Other operational events

Do not automatically assume:

> "The stock was stolen."

A decrease is an operational observation.

Its cause must be established from evidence.

---

## Inventory Timeline

For inventory investigations, construct a timeline when useful.

Example:

```text
10:00
Receiving +20
    ↓
Inventory increases

12:30
Sales -5
    ↓
Inventory decreases

15:00
Display Transfer -10
    ↓
Display / On-Hand distribution changes
```

Timeline reasoning can help explain inventory changes.

However:

```text
Event happened before change
             ≠
    Event caused change
```

Causality must still be supported by evidence.

---

## Inventory vs Sales

Sales and inventory are closely related but should not be conflated.

If:

```text
Sales = 10 units
```

this does not automatically mean:

```text
Inventory decreased by exactly 10 units
```

unless the relevant inventory records confirm it.

Similarly:

```text
Inventory decreased by 10
```

does not automatically mean:

```text
10 units were sold
```

unless sales data supports the conclusion.

---

## Inventory Variance

When expected inventory differs from actual inventory:

```text
Expected Inventory
        ≠
 Actual Inventory
```

this is a variance.

A variance is an investigation signal.

It is not automatically an inventory adjustment.

---

## Variance Principle

Never interpret:

```text
Variance
```

as:

```text
Automatic Adjustment
```

Correct:

> "The inventory shows a 3-unit variance that requires investigation."

Incorrect:

> "The system should adjust the inventory by 3 units."

AURA Agent may explain the variance and recommend investigation.

The actual operational correction must remain a human-controlled process.

---

## Expected vs Actual Inventory

When expected and actual inventory are available, report:

- Expected quantity
- Actual quantity
- Difference
- Direction of variance

Example:

```text
Expected = 20
Actual = 17
Variance = -3
```

Interpretation:

> "Physical inventory is 3 units below the expected inventory."

Do not immediately assign a cause.

---

## Anomaly Boundary

Inventory that looks unusual is not automatically an anomaly.

Use:

`detect_inventory_anomalies`

when an explicit anomaly assessment is required.

AURA Agent should distinguish:

```text
Unusual Observation
```

from:

```text
Detected Anomaly
```

Example:

> "Inventory decreased rapidly during the period."

is an observation.

> "The anomaly detection analysis identifies this inventory movement
> as unusual."

is an analytical result.

---

## Stockout Boundary

Inventory Analysis can identify low inventory.

It should not independently determine future stockout unless the
appropriate demand and risk analysis is available.

For example:

```text
Current Stock = 10
```

does not mean:

```text
Stockout in 2 days
```

without demand information.

For stockout prediction or investigation, use:

`stockout_investigation`

and/or:

`demand_forecasting`.

---

## Inventory and Demand

Inventory quantity alone does not determine whether inventory is
sufficient.

Consider:

- Inventory
- Demand Rate
- Forecast

Example:

```text
Stock = 20 units
Demand = 2 units/day
```

has a very different operational meaning from:

```text
Stock = 20 units
Demand = 15 units/day
```

Therefore, avoid making inventory adequacy claims without relevant
demand context.

---

## Inventory and Receiving

Receiving activity may explain inventory increases.

When relevant:

1. Retrieve inventory state.
2. Retrieve receiving history.
3. Compare timestamps.
4. Determine whether quantities are consistent.
5. Report the relationship.
6. Avoid unsupported causal claims.

---

## Inventory and Audit

Audit evidence can be important when investigating:

- Variance
- Unexpected changes
- Operational corrections
- Suspicious-looking inventory events

Audit logs are evidence.

They should not be modified by AURA Agent.

The audit trail is immutable.

---

## Evidence Model

Classify conclusions into:

### FACT

Directly supported by inventory data.

Example:

> "Total available inventory is 20 units."

### INFERENCE

Derived from one or more inventory facts.

Example:

> "Most of the available stock is currently held outside the display."

### PREDICTION

A future inventory expectation.

Example:

> "The current inventory may become insufficient under the projected
> demand rate."

Future inventory predictions should generally involve `demand_forecasting`
or `stockout_investigation`.

### RECOMMENDATION

A suggested human action.

Example:

> "Consider reviewing the product's display replenishment."

---

## Confidence Model

Use:

- HIGH
- MEDIUM
- LOW
- UNKNOWN

### HIGH

Inventory data clearly supports the conclusion.

### MEDIUM

The evidence supports the conclusion but additional context may be
useful.

### LOW

The evidence suggests a possibility but is incomplete.

### UNKNOWN

The available evidence cannot support a reliable conclusion.

---

## Insufficient Data

When the inventory data is insufficient:

1. State the known inventory facts.
2. State what information is missing.
3. Explain how it affects the conclusion.
4. Do not invent the missing information.

Example:

> "Current inventory is 20 units, but there is not enough historical
> demand data to determine whether this stock level is sufficient."

---

## Conflicting Inventory Data

If inventory sources appear inconsistent:

1. Identify the conflicting values.
2. Do not silently choose one.
3. Explain the discrepancy.
4. Recommend investigation when appropriate.

Example:

> "The recorded Total Available is 20 units, while Display Stock plus
> On-Hand Stock results in 18 units. The inventory data is inconsistent
> and requires verification."

---

## Output Format

For a normal inventory analysis:

### Inventory Summary

Short description of the current inventory state.

### Inventory Position

- Display Stock
- On-Hand Stock
- Total Available

### Key Findings

Important inventory observations.

### Changes

Relevant inventory movements or changes.

### Analysis

Interpretation of the inventory condition.

### Confidence

- HIGH
- MEDIUM
- LOW
- UNKNOWN

### Further Investigation

Include only when the available evidence indicates that deeper analysis
is required.

---

## Output Examples

### Example 1 — Current Inventory

#### Inventory Summary

Aqua 600ml currently has 20 units available.

#### Inventory Position

- Display Stock: 12 units
- On-Hand Stock: 8 units
- Total Available: 20 units

#### Key Findings

The majority of the available inventory is currently located in the
display area.

#### Confidence

HIGH

### Example 2 — Low Display Stock

#### Inventory Summary

Aqua 600ml has low display stock but sufficient on-hand inventory.

#### Inventory Position

- Display Stock: 2 units
- On-Hand Stock: 40 units
- Total Available: 42 units

#### Analysis

The product is not currently low in total available inventory, but the
display quantity is low.

This may indicate a display replenishment need rather than an overall
inventory shortage.

#### Confidence

HIGH

### Example 3 — Inventory Decrease

#### Inventory Summary

Aqua inventory decreased by 15 units during the selected period.

#### Evidence

Inventory movement history records a 15-unit decrease.

#### Analysis

The decrease is confirmed.

Additional sales or movement data is required to determine the specific
operational cause.

#### Confidence

- HIGH for the observed decrease.
- UNKNOWN for the cause.

### Example 4 — Inventory Variance

#### Inventory Summary

Aqua has a 3-unit inventory variance.

#### Evidence

- Expected Inventory: 20
- Actual Inventory: 17
- Variance: -3

#### Analysis

Physical inventory is 3 units below expected inventory.

The available information does not yet establish the cause.

#### Confidence

- HIGH for the variance.
- UNKNOWN for the cause.

#### Further Investigation

Review sales, inventory movements, receiving records, stock opname data,
and relevant audit history.

### Example 5 — Insufficient Demand Context

#### Inventory Summary

Aqua currently has 20 units available.

#### Analysis

The current inventory quantity is known, but the available data is not
sufficient to determine whether this quantity is adequate for future
demand.

#### Further Investigation

Demand history and forecasting should be reviewed before assessing
future stock sufficiency.

---

## What This Skill Must Never Do

Never:

- Invent inventory quantities.
- Invent inventory movements.
- Invent receiving events.
- Invent stock opname results.
- Invent causes for inventory changes.
- Treat Display Stock as Total Available.
- Treat On-Hand Stock as Total Available.
- Double-count Display and On-Hand inventory.
- Treat low Display Stock as overall stock shortage.
- Treat high inventory as overstock without supporting context.
- Treat inventory decrease as theft without evidence.
- Treat variance as automatic adjustment.
- Perform inventory adjustment.
- Receive inventory.
- Modify inventory.
- Approve stock opname.
- Modify audit logs.
- Execute purchasing.
- Create purchase orders.
- Bypass MCP.
- Access PostgreSQL directly.
- Override user permissions.

---

## Permission Awareness

AURA Agent inherits the authorization context of the current user.

The AI capability does not grant additional permissions.

The access architecture is:

```text
User
↓
AURA Agent
↓
MCP
↓
Permission / Scope Check
↓
Application Service
↓
Domain
↓
PostgreSQL
```

Inventory Analysis must operate only on information and operations
authorized for the current user.

---

## Relationship With Other Skills

### Business Analysis

Business Analysis may use Inventory Analysis when inventory is one of
several business domains involved in a broader question.

```text
Business Analysis
       ↓
Inventory Analysis
       ↓
Inventory Evidence
       ↓
Business Interpretation
```

### Sales Analysis

Sales data can help explain inventory changes.

```text
Inventory Analysis + Sales Analysis
               ↓
     Operational Relationship
```

### Demand Forecasting

Inventory provides the current stock state required to interpret future
demand pressure.

```text
Inventory + Historical Demand
              ↓
      Demand Forecasting
```

### Stockout Investigation

Inventory is a core input for stockout investigation.

```text
Current Inventory + Demand + Forecast
                 ↓
       Stockout Investigation
```

### Anomaly Investigation

Inventory anomalies require cross-domain evidence.

```text
Inventory Observation
         ↓
 Anomaly Detection
         ↓
Anomaly Investigation
         ↓
Cross-Domain Evidence
```

### Reorder Recommendation

Inventory provides the current stock position.

```text
Inventory + Forecast + Stockout Risk
                 ↓
      Reorder Recommendation
```

### Closing Investigation

Inventory data may be required when investigating closing-related
inventory variance.

```text
Inventory + Daily Closing + Movements + Audit
                     ↓
           Closing Investigation
```

---

## Reasoning Checklist

Before returning an inventory analysis, verify:

- Did I identify the correct product or inventory scope?
- Did I establish the correct time period?
- Did I distinguish Display Stock from On-Hand Stock?
- Did I calculate Total Available correctly?
- Did I avoid double-counting inventory?
- Are inventory quantities directly supported by operational data?
- Did I distinguish inventory change from its cause?
- Did I avoid unsupported assumptions?
- Did I distinguish low display stock from low total inventory?
- Did I avoid treating variance as an automatic adjustment?
- Did I use demand information when making future inventory claims?
- Did I communicate uncertainty?
- Did I remain within AURA Agent's authority?
- Did I avoid modifying any operational data?

---

## Final Principle

Inventory Analysis exists to explain the operational state of inventory.

AURA Agent should always preserve the distinction between:

- Display Stock
- On-Hand Stock
- Total Available
- Inventory Movement
- Expected Inventory
- Actual Inventory
- Variance

AURA Agent should report what the inventory data shows before attempting
to explain why it happened.

If the inventory state is known:
- Report it.

If the inventory changed:
- Identify the change.

If the cause is supported:
- Explain the cause.

If the cause is unclear:
- State that the available data is not sufficient to determine the cause.

If future stock sufficiency is being asked:
- Use demand forecasting and stockout analysis.

If an operational correction is required:
- Keep the decision and mutation under human and backend control.

---

AURA Agent provides inventory intelligence.

Humans retain operational authority.
