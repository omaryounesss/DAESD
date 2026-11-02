# Traceability: i* → Strategic BPMN → Operational BPMN → Camunda

| | |
|---|---|
| **Project** | Online Food Marketplace – UFCFTR-30-3, Assessment Task 1 |
| **Use case** | Use Case 1 – Producer Product Listing and Inventory Management |
| **Backlog item** | E3-06 (lead: Omar Younes, with Mohamed Alabweh and Zaineldin Sharaf) |
| **Sprint** | 2 |
| **Status** | Draft. The i\* and strategic BPMN columns are complete. The operational BPMN and Camunda columns are **planned names** to be confirmed by Zaineldin Sharaf (M3) and Omar Abdelaaty (M4) as their models are built. |
| **Related artefacts** | [case-study-analysis.md](case-study-analysis.md) · [selected-functionalities.md](selected-functionalities.md) · [i\* models](../models/i-star/) · [strategic BPMN](../models/strategic-bpmn/) |

---

## 1. Purpose

The brief asks for a clear progression: **i\* SD/SR → strategic BPMN → operational BPMN → Camunda**. This table shows how each stakeholder need in our analysis is carried through every level, so any element can be traced back to why it exists and forward to where it is implemented.

**Rule for the whole team:** use the **same names** at every level. Where an operational task or Camunda element is named below, please use that name (or tell Mohamed Alabweh so the i\* model can be updated to match).

## 2. How to read the tables

- **Need** is the stakeholder dependency or tension from the case-study analysis (§3.3, §3.4).
- **i\*** names the element in the SD or SR model ([models/i-star](../models/i-star/)).
- **Strategic BPMN** names the element in `strategic-marketplace.bpmn`.
- **Operational BPMN** and **Camunda** give the planned element, based on the agreed scope in `selected-functionalities.md`.
- **Rule** is the business rule from §5 of the case-study analysis.

## 3. Functionality 1: Product listing, validation and publication

| # | Need (analysis) | i\* (SD / SR) | Strategic BPMN | Operational BPMN (planned) | Camunda (planned) | Rule |
|---|---|---|---|---|---|---|
| 1.1 | Producer depends on Platform for *Product published* (§3.3) | SD dependency *Product published*; SR goal **Product published**, achieved by task **Process product listing** | Sub-process *Manage product listings*; start event *Product details received* | Process **Product listing, validation and publication**; end event *Product published* | Executable listing process | BR-01 |
| 1.2 | Platform depends on Producer for *Product details* (§3.3) | SD/SR dependency *Product details*; SR task **Submit product details** (Producer) | Message flow *Product details* (Producer → Platform) | User task **Submit product details** (Producer lane) | Camunda Form *Product details* (name, category, price, quantity, origin, harvest date, allergens, organic claim, best-before) | BR-01 |
| 1.3 | Accurate product information | SR task **Validate product details** → helps *Accurate product information* | Inside *Manage product listings* | Business rule / service task **Validate product details**; gateway *Details valid?* | Validation logic on form variables; gateway condition | BR-01 |
| 1.4 | Producer depends on Platform for *Easy listing process* (§3.3); tension: list quickly vs complete data (§3.4) | SD/SR dependency *Easy listing process* (quality) | – (design quality, not a strategic element) | Exception path: user task **Correct product details** with the validation messages | Form shows clear, field-level error messages | BR-01, BR-03 |
| 1.5 | Platform depends on certification service for *Organic claims verified* (§3.3) | SD/SR dependency *Organic claims verified*; SR goal **Organic claim verified**, task **Check with certification service** | Message flows *Certification check request* / *Certification result* (Organic Certification Service pool) | Gateway *Organic claimed?*; service task **Check with certification service**; gateway *Certification passed?* | Service task calling the simulated certification service (built by Mohamed Hamdy, M5) | BR-02 |
| 1.6 | Customer depends on Platform for *Honest (verified) organic claims* (§3.3) | SD/SR dependency *Honest (verified) organic claims* → quality **Trustworthy organic labelling** | – | *Certification passed?* = no → product cannot be published as organic | Gateway condition on the certification result variable | BR-02 |
| 1.7 | Tension: waiting for an unavailable service protects trust but delays sales (§3.4) | SR task **Request manual review** (helps *Trustworthy organic labelling*, hurts *Fast listing*); SD/SR dependency *Flag unverified listings for review* (Administrator) | Administrator lane | Error boundary event on **Check with certification service** → retry → user task **Review unverified listing** (Administrator lane) | Error boundary event, retry, and an Administrator user task with a review Form | BR-03 |
| 1.8 | Product stored for customers and traceability | SR task **Save product to catalogue**, resource **Product catalogue** | Data stores *Product catalogue* and *Traceability records* | Service task **Save product to catalogue**; data stores *Product catalogue* and *Traceability records* | Process variables written to the catalogue; origin, allergen and best-before recorded | BR-01, BR-10 |

## 4. Functionality 2: Inventory and seasonal availability management

| # | Need (analysis) | i\* (SD / SR) | Strategic BPMN | Operational BPMN (planned) | Camunda (planned) | Rule |
|---|---|---|---|---|---|---|
| 2.1 | Customers must only see products they can buy | SR goal **Availability kept accurate**, achieved by task **Update availability automatically** | Sub-process *Manage inventory and availability*; end event *Stock status updated* | Process **Inventory and seasonal availability**; end event *Stock status updated* | Executable inventory process | BR-04, BR-05 |
| 2.2 | Platform depends on Producer for *Up-to-date stock and season data* (§3.3) | SD/SR dependency *Up-to-date stock and season data*; SR goal **Stock kept accurate** (Producer); task **Read stock and season updates** (Platform) | Message flow *Stock and season update*; start event *Stock or season update received* | User task **Update stock and season** (Producer lane) | Camunda Form *Stock and season update* (quantity, season start, season end) | BR-04, BR-05 |
| 2.3 | Tension: producers also sell offline, so stock drifts (§3.4) | SR task **Make unavailable at zero stock** (helps *Accurate availability*); Producer trade-off *Update after each sale* vs *Update stock weekly* | Inside *Manage inventory and availability* | Gateway *Stock at zero?* → service task **Make unavailable at zero stock** | Gateway condition on the quantity variable | BR-04 |
| 2.4 | Restocked products only sold in season | SR task **Check season dates** (helps *Accurate availability*) | Inside *Manage inventory and availability* | Gateway *Within season?*; timer events at season start and end (agreed F2 addition) | Gateway condition on season dates; timer events | BR-05 |

## 5. Gaps to close

Checking the levels against each other found these gaps. Each has an owner.

| # | Gap | Where | Action | Owner |
|---|---|---|---|---|
| G1 | The agreed F2 additions (low-stock alert via the notification service, rejected stock updates, "order paid – reduce stock" message start) are not yet in the i\* SR model. | i\* SR | Add a task *Send low-stock alert* depending on the Notification service, and a task *Reject invalid update* to the Platform. | Mohamed Alabweh |
| G2 | In the strategic BPMN, *Process orders and payments* only reads the *Product catalogue*; nothing shows a paid order reducing stock. | Strategic BPMN | Make the data association two-way, or note it as the Task 2 integration point. | Omar Younes |
| G3 | Operational task names are planned, not built. | Operational BPMN | Use the names in sections 3 and 4, or report changes so i\* can match. | Zaineldin Sharaf |
| G4 | Camunda element names and variables are planned, not built. | Camunda | Use the names in sections 3 and 4 for tasks, Forms and variables. | Omar Abdelaaty |
| G5 | The certification-service fallback is worded differently in two documents ("retry, then administrator" vs "manual review or listing without the organic claim"). | Analysis / functionalities | Agree one fallback. This table assumes retry, then administrator review. | Omar Younes, Zaineldin Sharaf |

## 6. Keeping this table current

Update this table whenever a name changes at any level, in the same pull request as the change. Before each sprint review, check every row has a real element in every column.
