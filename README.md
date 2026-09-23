# 🎯 Customer Revenue Opportunity Engine

**Customer lifecycle intelligence for prioritizing sales outreach**

[🚀 Launch the Live Demo](https://alex-customer-revenue.streamlit.app/)

A Python and Streamlit portfolio project that converts multi-year customer purchase history into an explainable sales-action queue using recency, revenue decline, purchase cadence, inactivity, and customer-value signals.

> **Portfolio edition:** This repository uses 100% synthetic data. It contains no employer, customer, contact, pricing, or proprietary sales records.

---

## The Business Problem

Customer transaction history can become a large list of names and purchases without giving a sales team much guidance about where to focus next.

Typical questions include:

- Which customers deserve immediate review?
- Which high-value accounts have gone quiet?
- Which customers show material recent revenue decline?
- Which repeat buyers appear due for another purchase?
- Which dormant customers are worth re-engaging?
- How can outreach be prioritized consistently across reps and locations?

The Customer Revenue Opportunity Engine turns those questions into a repeatable, transparent prioritization workflow.

---

## 🚀 Live Demo

### [Launch the Customer Revenue Opportunity Engine →](https://alex-customer-revenue.streamlit.app/)

The live app includes:

- Executive opportunity KPIs
- A / B / C priority segments
- Purchase-cycle signals
- Revenue-decline signals
- Dormancy and inactivity analysis
- Sales-rep opportunity views
- Store-level opportunity views
- Customer signal diagnostics
- Downloadable sales-action queue

---

## What the Engine Does

The application:

1. Aggregates multi-year transaction history to the customer level.
2. Measures recency, frequency, and lifetime revenue.
3. Compares recent 12-month revenue with the prior 12 months.
4. Calculates historical days between repeat purchases.
5. Detects purchase-cycle, decline, inactivity, and dormancy signals.
6. Identifies higher-value customer populations.
7. Combines those signals using transparent prioritization rules.
8. Produces a management-ready sales-action queue.

---

## Opportunity Segments

The engine uses explainable segments rather than a black-box score.

### A-DUAL

High-value customer with both:

- a purchase-cycle signal, and
- a material recent revenue-decline signal.

### A-CYCLE

High-value repeat customer whose historical purchase cadence suggests another purchase may be due.

### A-DECLINE

High-value customer with a material recent revenue decline.

### B-CYCLE

Repeat-purchase cadence suggests a reasonable follow-up opportunity.

### B-DECLINE

Recent revenue is materially below the prior 12-month period.

### B-INACTIVE

Customer has not purchased within the last 12 months.

### C-NURTURE

No stronger action signal is currently present. Maintain the relationship and monitor future behavior.

---

## Core Analytical Signals

### Recency

```text
Analysis Date - Last Purchase Date
```

This measures how long the customer has been inactive.

### Frequency

The engine tracks the number of observed purchases in the available history.

### Customer Value

Customer value is evaluated using metrics such as:

```text
Lifetime Revenue
Average Purchase Value
Maximum Purchase Value
```

### Revenue Decline

The engine compares:

```text
Current 12-Month Revenue
vs.
Prior 12-Month Revenue
```

A material decline becomes a review signal rather than an automatic churn label.

### Purchase Cadence

For repeat buyers, the engine measures historical time between purchases:

```text
Average Purchase Interval
Median Purchase Interval
```

It then compares current recency with historical cadence to identify customers who may be approaching or exceeding a typical repurchase window.

---

## Reference Opportunity Value

The dashboard includes a field called:

```text
Reference Opportunity Value
```

This is deliberately **not** called:

- forecast revenue,
- expected revenue,
- recoverable revenue,
- or guaranteed sales.

It is a prioritization reference derived from the customer's historical purchase behavior.

For decline cases, it can consider the gap between prior and recent revenue.

For other opportunities, it can use historical average purchase value as a practical reference point.

This keeps the output useful without overstating what historical customer behavior can predict.

---

## Analytical Guardrails

The engine intentionally avoids several common overclaims.

A priority segment does **not** mean:

- the customer will definitely buy,
- a dormant customer has permanently churned,
- a decline is caused by lost loyalty,
- or the reference opportunity value will be realized.

Observed behavior may be influenced by:

- seasonality,
- inventory availability,
- economic conditions,
- product replacement cycles,
- promotions,
- relationship changes,
- or purchases made elsewhere.

The dashboard is designed for **sales prioritization and review**, not automated customer decisions.

---

## Architecture

```text
Synthetic Customer Purchase History
                |
                v
        Data Validation
                |
                v
       Customer Aggregation
                |
                v
   Recency / Frequency / Value
          /         |         \
         v          v          v
 Revenue Decline  Purchase   Dormancy
                  Cadence
         \          |          /
          \         |         /
           v        v        v
        Opportunity Signals
                |
                v
     Transparent Priority Rules
                |
                v
     A / B / C Action Queue
          /             \
         v               v
   Sales Rep View     Store View
                |
                v
       Downloadable Queue
```

---

## Technology

- **Python**
- **pandas**
- **NumPy**
- **Streamlit**
- Deterministic synthetic-data generation
- Customer lifecycle analytics
- Revenue trend analysis
- Purchase-cycle analysis
- Rule-based prioritization
- Revenue operations decision support

---

## Repository Structure

```text
customer-revenue-opportunity-engine/
├── app.py
├── engine/
│   ├── __init__.py
│   ├── analysis.py
│   └── demo_data.py
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

## Run Locally

Clone the repository:

```bash
git clone https://github.com/amonday3-ai/customer-revenue-opportunity-engine.git
cd customer-revenue-opportunity-engine
```

Create a virtual environment:

```bash
python -m venv .venv
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Launch the app:

```bash
streamlit run app.py
```

---

## Data Safety

This public repository deliberately contains **no real customer data**.

It does not include:

- customer names,
- email addresses,
- phone numbers,
- physical addresses,
- real company accounts,
- real purchase histories,
- proprietary pricing,
- internal revenue figures,
- or employer records.

All demonstration data is generated deterministically in:

```text
engine/demo_data.py
```

using fictional:

- customers,
- companies,
- stores,
- sales representatives,
- products,
- purchase dates,
- and transaction values.

---

## What This Project Demonstrates

This project is designed to show the ability to:

- translate customer history into sales-prioritization logic,
- distinguish observable signals from predictions,
- analyze revenue decline without overclaiming churn,
- detect repeat-purchase patterns,
- combine multiple customer signals transparently,
- create actionable sales queues,
- summarize opportunities by rep and location,
- build executive-facing dashboards,
- and communicate analytical limitations clearly.

---

## Potential Production Enhancements

A production implementation could add:

- CRM integration,
- automated weekly refreshes,
- product-affinity modeling,
- customer lifetime value forecasting,
- contact-history integration,
- salesperson follow-up tracking,
- campaign-response measurement,
- service-history signals,
- next-best-product recommendations,
- and closed-loop opportunity conversion reporting.

---

## Author

### Alex Monday

**Business Intelligence • ERP/Data Administration • Python Automation • Revenue Operations**

[Live Demo](https://alex-customer-revenue.streamlit.app/)  
[GitHub Repository](https://github.com/amonday3-ai/customer-revenue-opportunity-engine)
