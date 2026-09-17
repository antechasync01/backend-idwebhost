# Supplier Recommendation Skill

## Purpose

The Supplier Recommendation skill enables AURA Agent to identify, evaluate, and recommend appropriate suppliers for store replenishment, providing verified vendor contact details, linked product catalogs, and historical receiving reliability.

Questions answered:
- Which supplier provides Product X?
- What is the WhatsApp or phone contact for Supplier Y?
- Which supplier should the Owner contact for urgent product replenishment?
- What catalog items are linked to a specific vendor?
- Does historical delivery data support using this supplier for urgent orders?

This skill provides vendor intelligence. It does not execute purchase orders, send messages to suppliers, or negotiate commercial terms.

---

## When to Use

Use when the user inquires about vendor options, supplier details, or contact channels for purchasing:

### Vendor Identification
- "Which supplier provides Aqua 600ml?"
- "Who is our distributor for Indofood products?"
- "Show me all suppliers linked to our dairy category."

### Contact & Outreach Preparation
- "Give me the WhatsApp contact for PT Sumber Tirta."
- "Who is the contact person for our snack vendor?"
- "Prepare vendor contact information for today's reorder."

### Vendor Comparison
- "Which supplier has the most reliable delivery history for cooking oil?"
- "Compare suppliers linked to instant noodles."

---

## When Not to Use

Route non-supplier inquiries to their specialized skills:
- Calculating optimal reorder quantity and order sizing → `reorder_recommendation`
- Placing external purchase orders or sending WhatsApp messages → External Manual Task (Owner responsibility)
- Creating, editing, or deleting supplier profiles in settings → Manual Owner CRUD
- Diagnosing delivery delays after a stockout → `stockout_investigation`
- Checking warehouse stock balances → `inventory_analysis`

---

## Required Context

Identify before generating recommendations:
- Target Product or Category: SKU, product name, or product family
- Target Supplier: Name or ID if investigating a specific vendor
- Reorder Urgency: Routine scheduled replenishment vs urgent stockout mitigation
- Supplier Master Data: Contact person, phone, WhatsApp number, address, notes
- Historical Receiving Records: Delivery logs, receipt statuses, fulfillment notes

---

## MCP Tools

Use only authorized PRD tools:

### READ Tools
- `get_supplier`: Retrieve supplier master profile (name, contact person, phone, WhatsApp, address, notes).
- `get_supplier_products`: Fetch products linked to a supplier, or suppliers linked to a product.
- `get_receivings`: Review historical delivery records, receipt dates, and delivery notes.
- `get_product` / `get_products`: Check product catalog information and current category mappings.
- `get_inventory`: Check current stock status of linked products.

### RECOMMEND Tools
- `generate_supplier_contact_recommendation`: Format structured vendor contact recommendations for Owner.
- `generate_reorder_recommendation`: Handoff to order quantity sizing when needed.

---

## Reasoning Procedure

1. **Identify Target Scope**: Determine the target product or supplier under review.
2. **Retrieve Linked Vendors**:
   Call `get_supplier_products` to find all registered suppliers associated with the product:
```text
Product ───(linked via)─── Supplier Products ───(maps to)─── Supplier Profile
```
3. **Fetch Full Vendor Profiles**:
   Call `get_supplier` for each candidate vendor to extract contact person, WhatsApp, phone, and operational notes.
4. **Evaluate Receiving History**:
   Query `get_receivings` for past shipments from the candidate suppliers:
   - Check frequency of completed deliveries.
   - Check for logged delivery notes regarding delays or fulfillment issues.
   - Do NOT invent pricing or delivery speed not recorded in system data.
5. **Formulate Primary Recommendation**:
   - If one supplier is mapped, present complete verified contact details.
   - If multiple suppliers exist, rank by verified delivery history and catalog relevance.
6. **Structure Actionable Output**: Provide direct WhatsApp/phone contact details and remind the Owner to initiate external communication.

---

## Evidence Requirements

| Recommendation Component | Required MCP Evidence |
| :--- | :--- |
| Product-Supplier Link | `get_supplier_products` active relationship record |
| Contact Details | `get_supplier` master record (phone, WhatsApp, name) |
| Delivery Reliability | `get_receivings` confirmed historical deliveries |

Strict Data Integrity Rule:
Never fabricate supplier pricing, discounts, credit terms, minimum order quantities, or delivery times unless explicitly recorded in supplier notes or receiving logs.

If no supplier is linked to a product:
> "No active supplier is linked to this product in the system."

---

## Uncertainty Handling

- **Missing Contact Fields**: If phone or WhatsApp is blank in the supplier record, explicitly note the missing field and recommend updating Supplier Settings.
- **No Historical Receiving Data**: For newly linked suppliers without receiving history, state that delivery performance is unrated.
- **Multiple Unrated Suppliers**: Present all linked suppliers neutrally with available contact data, leaving selection to the Owner.

---

## Output Format

```markdown
## Recommendation Summary
[Concise summary identifying the recommended supplier and primary contact channel]

## Supplier Profile
- Supplier Name: [Company Name]
- Contact Person: [Name / Title]
- WhatsApp / Phone: [Phone Number]
- Address / Location: [Address notes]
- Operational Notes: [Special ordering notes, delivery days, etc.]

## Linked Products & Status
- Target Product: [Product Name] (Current Stock: [X] units)
- Other Supplied SKUs: [List of key co-supplied products]

## Historical Delivery Performance
- Total Completed Deliveries: [N] shipments
- Last Received Date: [YYYY-MM-DD]
- Delivery Notes: [Timeliness or receiving observations from records]

## Confidence
[HIGH | MEDIUM | LOW | UNKNOWN] — [Brief justification]

## Recommended Owner Action
[Clear instructions for Owner to reach out via WhatsApp or phone externally]
```

---

## Examples

### Example 1: Single Linked Supplier for Urgent Restock

```markdown
## Recommendation Summary
Contact PT Sumber Tirta Lestari via WhatsApp for replenishment of Aqua 600ml.

## Supplier Profile
- Supplier Name: PT Sumber Tirta Lestari
- Contact Person: Pak Hendra (Sales Representative)
- WhatsApp / Phone: 0812-3456-7890
- Address: Pergudangan Daan Mogot Blok C-12, Jakarta Barat
- Operational Notes: Next-day delivery available for orders placed before 14:00.

## Linked Products & Status
- Aqua 600ml (Current Stock: 14 units — Critical Reorder)
- Aqua 1500ml (Current Stock: 28 units — Normal)
- Vit 600ml (Current Stock: 32 units — Normal)

## Historical Receiving Performance
- Total Completed Deliveries: 14 shipments (`get_receivings`)
- Last Received Date: 2026-09-02 (Received full order of 48 units on time)
- Delivery Notes: Consistent on-time delivery record.

## Confidence
HIGH — Directly verified supplier catalog link and active receiving history.

## Recommended Owner Action
Owner should contact Pak Hendra via WhatsApp (0812-3456-7890) to place an order for Aqua 600ml (recommended quantity: 48 units).
```

### Example 2: Selecting Between Multiple Linked Suppliers

```markdown
## Recommendation Summary
Recommend CV Pangan Sejahtera as primary vendor for Indomie Goreng due to established delivery history.

## Supplier Profile
- Supplier Name: CV Pangan Sejahtera (Primary)
- Contact Person: Ibu Rina
- Phone / WhatsApp: 0811-9876-5432
- Alternative Supplier: PT Distribusi Sembako Nusantara (Phone: 021-555-8899)

## Linked Products & Status
- Indomie Goreng Special (Current Stock: 22 units — Low)
- Indomie Kuah Soto (Current Stock: 30 units — Normal)

## Historical Receiving Performance
- CV Pangan Sejahtera: 8 completed deliveries in last 60 days, average turnaround 2 days.
- PT Distribusi Sembako: 1 delivery on record (35 days ago), no recent activity.

## Confidence
HIGH — Supported by comparative receiving logs.

## Recommended Owner Action
Owner should reach out to Ibu Rina at CV Pangan Sejahtera for replenishment.
```

---

## What This Skill Must Never Do

- Never place orders, send messages, or sign purchasing commitments.
- Never create Purchase Orders or internal purchasing contracts.
- Never invent supplier prices, discounts, or delivery guarantees.
- Never modify supplier master records or link mappings directly.
- Never bypass the MCP gateway to access PostgreSQL directly.

---

## Relationship With Other Skills

```text
              supplier_recommendation
                         │
     ┌───────────────────┼───────────────────┐
     ▼                   ▼                   ▼
reorder_recommendation stockout_investigation inventory_analysis
(Uses supplier data   (Checks supplier       (Checks stock of
 for order proposals)  delivery history)      co-supplied goods)
```

- `reorder_recommendation`: Consumes supplier profile to complete reorder proposals.
- `stockout_investigation`: Cross-checks vendor delivery history when investigating stockouts.
- `inventory_analysis`: Validates stock across all SKUs linked to a supplier for consolidated ordering.

---

## Reasoning Checklist

- [ ] Did I verify the product-to-supplier link via `get_supplier_products`?
- [ ] Did I extract active contact details from `get_supplier`?
- [ ] Did I check past delivery history via `get_receivings`?
- [ ] Did I avoid fabricating pricing, terms, or delivery speed?
- [ ] Did I state the limitation phrase if no supplier is linked?
- [ ] Did I remind the Owner that purchasing communication is an external manual action?

---

## Final Principle

Supplier recommendation provides vendor intelligence and actionable contact channels. AURA Agent identifies who to contact based on catalog links and receiving records; human owners initiate communication and finalize all commercial terms externally.
