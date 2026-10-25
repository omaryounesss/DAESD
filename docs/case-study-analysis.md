# Case-Study Analysis: Major Business Processes and Organisational Responsibilities

| | |
|---|---|
| **Project** | Online Food Marketplace – UFCFTR-30-3, Assessment Task 1 |
| **Use case** | Use Case 1 – Producer Product Listing and Inventory Management |
| **Authors** | Omar Younes (business processes), Mohamed Alabweh (actors and responsibilities) |
| **Sprint** | 1 – Strategic Process Analysis and Project Setup |
| **Related artefacts** | `models/strategic-bpmn/strategic-marketplace.bpmn` · `docs/selected-functionalities.md` |

---

## 1. Purpose and approach

This document analyses the case study at enterprise level, before any single use case is modelled in detail. It answers four questions:

1. **Who** takes part in the marketplace, and what is each party responsible for? (Section 3)
2. **What** major business processes does the marketplace run? (Section 4)
3. **Which rules** govern those processes? (Section 5)
4. **How** do the processes depend on each other and on shared data? (Sections 6 and 7)

**Approach.** We read the case study and the three use cases and extracted every actor, activity, decision, rule and external service mentioned. Related activities were grouped into business areas, using one test: does this group of activities have its own trigger and its own business outcome? Each business area became one process in the strategic BPMN. Each process was then assigned to the actor who carries it out, and the information exchanged between actors was recorded as message flows and shared data stores.

The analysis directly feeds the strategic BPMN model (Sprint 1), the i\* models (Sprint 2) and the scoping of our two major functionalities (`selected-functionalities.md`).

## 2. The enterprise and its value proposition

The marketplace is a **two-sided online platform** connecting local food **producers** with **customers**. It does not grow, store or deliver food. Its value lies in coordinating information, money and trust between the two sides:

| Party | What the marketplace offers them | What the marketplace needs from them |
|---|---|---|
| Producers | Access to customers; order handling; payment collection; settlement | Accurate product, stock and safety information; fulfilment of orders |
| Customers | One place to find and buy local produce from several producers in one order; confidence that product information is honest and safe | Orders, payment, reports of quality problems |
| The marketplace itself | Revenue from a **5% commission** on producer sales | Reliable payment, certification and notification services |

Because the marketplace sells food it does not handle, **trust and food safety** are its central obligations. It must be able to show that product claims (e.g. organic) are verified, and to trace which customers bought which product from which producer if a problem arises.

## 3. Actors and organisational responsibilities

### 3.1 Actors

| Actor | Type | Responsibilities | Main interests (feeds i\* goals) | Strategic BPMN |
|---|---|---|---|---|
| **Producer** | External participant | Lists products with accurate details (origin, allergens, harvest and best-before dates, certification); keeps stock and seasonal availability current; fulfils orders; responds to quality incidents | Sell produce; low admin effort; fair and timely payment | Pool |
| **Customer** | External participant | Searches, orders and pays; collects or receives orders; reports quality problems | Find suitable local food; trustworthy information; safe food; easy checkout | Pool |
| **Marketplace administrator** | Internal role (people) | Decisions needing human judgement: reviewing, escalating and closing food-quality incidents; overseeing exceptions | Platform reputation; regulatory compliance; fast incident response | Lane – Marketplace pool |
| **Marketplace platform** | Internal role (system) | Automated operations: validating and publishing listings, maintaining stock status, serving the catalogue, processing orders and payments, calculating commission, settling with producers, recording traceability data | Accurate, consistent, auditable data | Lane – Marketplace pool |
| **Payment provider** | External service | Takes customer payments; executes producer payouts | Valid payment instructions | Collapsed pool |
| **Organic-certification service** | External service | Confirms or rejects producers' organic certification claims; may be unavailable | Valid verification requests | Collapsed pool |
| **Notification service** | External service | Delivers order confirmations, alerts and incident notifications; delivery can fail | Valid recipients and messages | Collapsed pool |

### 3.2 Why actors are modelled this way

- **Producers and customers are separate pools**, not lanes, because they are independent parties. The marketplace can exchange messages with them but cannot control their internal work.
- **External services are collapsed (black-box) pools.** Only their interfaces (request and response) matter to the marketplace; their internal processes are outside our control and our scope.
- **The marketplace is split into an Administrator lane and a Platform lane** to separate decisions that need human judgement from automated processing. This split carries through to the operational models and Camunda, where it becomes user tasks versus service tasks.

### 3.3 Key dependencies between actors

These dependencies are the starting point for the i\* Strategic Dependency model in Sprint 2 (owner: Mohamed Alabweh, Member 2).

The *Type* column gives the i\* dependum type, which decides how each dependency is drawn in the SD model: a **goal** is an outcome that is either achieved or not, a **softgoal** is a quality with no clear-cut criteria, a **task** is a specific activity, and a **resource** is information or a physical item.

| Depender | Depends on | For | Type |
|---|---|---|---|
| Customer | Producer | Accurate product, allergen and origin information | Softgoal |
| Customer | Marketplace | Honest (verified) organic claims | Softgoal |
| Customer | Marketplace | Alerts if a product they bought is unsafe | Resource |
| Marketplace | Producer | Up-to-date stock and season data | Resource |
| Marketplace | Producer | Information during quality incidents | Resource |
| Marketplace | Organic-certification service | Organic claims verified | Goal |
| Marketplace | Payment provider | Payments collected and payouts made | Goal |
| Marketplace | Notification service | Reliable delivery of confirmations and alerts | Softgoal |
| Producer | Marketplace | Correct payment of their share, minus 5% commission | Goal |

### 3.4 Tensions between stakeholder goals

These conflicts are the trade-offs the i\* Strategic Rationale model reasons about. Each becomes a decision inside an actor's boundary, with contribution links to the softgoals it helps or hurts.

| Tension | Stakeholders | How our design responds |
|---|---|---|
| Producers want to list quickly; the marketplace needs complete, valid data. | Producer vs Marketplace | Strict validation of mandatory fields only, with clear correction messages (BR-01). |
| Waiting for an unavailable certification service protects trust but delays sales. | Customer, Producer vs Marketplace | Retry, then administrator review; never published as organic without a positive result (BR-02, BR-03). |
| Producers also sell offline, so platform stock can drift from real stock. | Producer vs Customer | Automatically unavailable at zero stock, plus low-stock alerts (BR-04). |
| Traceability needs customer data; data protection limits what is kept. | Marketplace vs Customer | Store only what traceability needs, for a defined period (BR-10). |

## 4. Major business processes

### 4.1 Summary

| # | Business area | Strategic BPMN element | Responsible | Trigger | Business outcome | External services | Use case |
|---|---|---|---|---|---|---|---|
| P1 | Product listing | *Manage product listings* | Platform | Producer submits product details | Product validated and published, or returned for correction | Organic-certification | UC1 |
| P2 | Inventory and seasonal availability | *Manage inventory and availability* | Platform | Producer updates stock or season | Availability always matches stock and season | – | UC1 |
| P3 | Browsing and searching | *Provide product catalogue and search* | Platform | Customer searches | Matching available products returned | – | UC2 |
| P4 | Ordering and payment | *Process orders and payments* | Platform | Customer checks out | Order paid, split per producer, confirmed | Payment, Notification | UC2 |
| P5 | Fulfilment (collection/delivery) | Producer: *Fulfil orders*; Customer: *Collect or receive order* | Producer | Producer receives its order | Customer receives the goods | – | UC2 |
| P6 | Producer settlement and commission | *Settle producer payments* | Platform | Paid orders | Producer paid their share minus 5% commission | Payment | UC2 |
| P7 | Food quality and traceability | *Manage food-quality incidents* | Administrator | Issue reported | Risk assessed; affected customers alerted; incident closed | Notification | UC3 |
| P8 | Community / surplus-food features | *To be added* | To confirm | To confirm | To confirm | To confirm | Base case study |

### 4.2 Process notes

**P1 Product listing.** The supply side of the enterprise. Validates mandatory information and has any organic claim verified externally before publication. It also captures the origin, allergen and date data that P7 later depends on.

**P2 Inventory and seasonal availability.** Keeps what customers can buy aligned with what producers can supply. It responds to producer updates and to stock reductions caused by P4.

**P3 Browsing and searching.** Read-only from the business point of view: it exposes published, available products from the shared catalogue.

**P4 Ordering and payment.** The revenue-generating process. One customer order may contain products from several producers, so P4 checks availability, takes a single payment, splits the order per producer and attributes each producer's share and the marketplace's 5% commission.

**P5 Fulfilment.** Carried out by producers, not the marketplace, so it is modelled in the Producer and Customer pools. The marketplace's part is passing each producer its order (message flow *Producer order*).

**P6 Settlement.** Pays producers what P4 attributed to them, minus commission, and provides a settlement statement.

**P7 Food quality and traceability.** Turns a report into action: identifies the product and producer, finds affected customers from order records, asks the producer for information, decides whether to escalate, alerts customers and closes the incident. It needs human judgement, so it sits in the Administrator lane.

**P8 Community / surplus-food features.** Identified in the group's initial reading of the case study but not described in the three use cases. It will be modelled once confirmed against the full case study with the module team (Section 9).

## 5. Business rules extracted from the case study

| ID | Rule | Applies to |
|---|---|---|
| BR-01 | A product cannot be published until all mandatory information is present and valid. | P1 |
| BR-02 | A product may only be described as organic if its certification has been verified. | P1 |
| BR-03 | If the verification service is unavailable or validation fails, the process must follow a defined alternative path rather than stop. | P1 |
| BR-04 | A product with zero stock is unavailable for new orders. | P2, P4 |
| BR-05 | A restocked product becomes available again only within its seasonal availability period. | P2 |
| BR-06 | At checkout, all items must still be available in the requested quantities; otherwise the customer amends the order. | P4 |
| BR-07 | A multi-vendor order is split into producer-specific parts. | P4, P5 |
| BR-08 | The marketplace takes 5% commission; each producer's share is calculated per order. | P4, P6 |
| BR-09 | A declined payment can be retried; a temporarily unavailable payment service triggers a retry/exception path. | P4 |
| BR-10 | Records must link customers, products and producers so affected customers can be contacted rapidly. | P1, P4, P7 |
| BR-11 | A confirmed safety issue suspends the product from further sale where appropriate. | P7, P2 |
| BR-12 | Each notification's outcome is recorded; failures trigger an alternative method or manual follow-up. | P7 |

## 6. How the processes depend on each other

The processes form one connected value chain rather than isolated features:

1. **Listing feeds everything (P1 → P3, P4).** Only published products appear in the catalogue and can be ordered. No listings means no sales and no commission.
2. **Ordering changes stock (P4 → P2).** A successful payment reduces stock; at zero, P2 makes the product unavailable (BR-04).
3. **Payment drives fulfilment and settlement (P4 → P5, P6).** Each paid order is split per producer, sent to that producer to fulfil, and later settled minus commission.
4. **Traceability ties listing, ordering and quality together (P1 + P4 → P7).** P1 records where a product came from and what it contains; P4 records who bought it. P7 combines both to alert every affected customer (BR-10).
5. **Incidents feed back into availability (P7 → P2).** A confirmed issue can suspend a product (BR-11).

In the strategic BPMN, these dependencies appear as message flows and three shared data stores:

| Data store | Written by | Read by | Supports |
|---|---|---|---|
| Product catalogue | P1, P2 | P3, P4 | BR-01, BR-04, BR-05 |
| Order records | P4 | P6 | BR-07, BR-08 |
| Traceability records | P1, P4 | P7 | BR-10 |

## 7. Responsibility matrix (RACI)

R = Responsible (does the work) · A = Accountable (owns the outcome) · C = Consulted · I = Informed.

| Process | Producer | Customer | Administrator | Platform | Payment | Certification | Notification |
|---|---|---|---|---|---|---|---|
| P1 Product listing | C | | A | R | | C | |
| P2 Inventory and availability | C | | A | R | | | |
| P3 Browsing and searching | | I | A | R | | | |
| P4 Ordering and payment | I | C | A | R | C | | I |
| P5 Fulfilment | R / A | I | | | | | |
| P6 Settlement | I | | A | R | C | | |
| P7 Food quality incidents | C | I | R / A | C | | | I |

The administrator is accountable for every marketplace process even where the platform performs the work. Automated processes still need a human owner for exceptions, audits and incidents.

## 8. Legal, ethical, social and professional considerations

These considerations shape the processes above and are evaluated further in Sprint 3.

- **Food information for distance selling.** Food sold online must have its mandatory food information, including allergens, available to the consumer before the purchase is concluded and again at delivery (Regulation (EU) No 1169/2011, as retained in UK law; Bridges and Tingle, 2020). This is why P1 must capture allergen and product details before a product can be published (BR-01).
- **Organic claims.** In the UK, "organic" can only be applied to products whose production and processing have been inspected and certified by an approved control body (Regulation (EU) 2018/848, as retained in UK law; Business Companion, no date). This justifies the certification check in P1 (BR-02).
- **Traceability.** Food businesses must be able to identify who supplied a food and to whom they supplied it, and must withdraw unsafe food from sale (Regulation (EC) No 178/2002, Articles 18–19, as retained in UK law). This is why P1 and P4 write to the traceability records and P7 can suspend a product (BR-10, BR-11).
- **Personal data.** Traceability (BR-10) requires storing who bought what. Under the UK GDPR and the Data Protection Act 2018, this data must be limited to what is needed, kept secure and retained only as long as necessary.
- **Payments.** Card handling is delegated to the payment provider, so the marketplace does not store payment card data. A sandbox or simulated service is used for this assessment.
- **Social and professional.** Supporting small local producers, being honest about product claims and responding quickly to safety issues are central to customer trust. Processes must be auditable so that decisions, such as why a product was suspended, can be explained.

## 9. Scope, assumptions and open questions

**Assumptions**

- Producers and customers are already registered; registration is not modelled.
- Fulfilment is performed by producers; the marketplace only coordinates it.
- External services are simulated for this assessment.

**Open questions (to confirm with the module team)**

1. Which community / surplus-food features does the full case study require, and should they form a separate process (P8)?
2. Should the strategic model show a direct message from producer to customer at fulfilment (e.g. "order ready / delivered")?

## 10. From analysis to functional scope

The analysis shows that **P1 Product listing** and **P2 Inventory and availability** form the supply side that every other process depends on:

- P3 and P4 consume their catalogue data.
- P4 changes their stock.
- P7 relies on the safety data that P1 captures.

They also contain an external service (P1), clear business rules (BR-01 to BR-05) and defined exception paths (BR-03). This is why the group selected them as its two major functionalities, as set out in `selected-functionalities.md`.

## References

Bridges, K. and Tingle, S. (2020) *Coronavirus: distance selling for UK food and hospitality businesses*. Pinsent Masons Out-Law Analysis, 25 March. Available from: https://www.pinsentmasons.com/en-gb/out-law/analysis/coronavirus-uk-food-distance-selling [Accessed 25 October 2026].

Business Companion (no date) *Labelling and describing organic food*. Available from: https://www.businesscompanion.info/en/quick-guides/food-and-drink/labellling-and-describing-organic-food [Accessed 25 October 2026].

Data Protection Act 2018, c. 12. Available from: https://www.legislation.gov.uk/ukpga/2018/12/contents [Accessed 25 October 2026].

Regulation (EC) No 178/2002 of the European Parliament and of the Council of 28 January 2002 laying down the general principles and requirements of food law (assimilated law). Available from: https://www.legislation.gov.uk/eur/2002/178/contents [Accessed 25 October 2026].

Regulation (EU) No 1169/2011 of the European Parliament and of the Council of 25 October 2011 on the provision of food information to consumers (assimilated law). Available from: https://www.legislation.gov.uk/eur/2011/1169/contents [Accessed 25 October 2026].

Regulation (EU) 2018/848 of the European Parliament and of the Council of 30 May 2018 on organic production and labelling of organic products (assimilated law). Available from: https://www.legislation.gov.uk/eur/2018/848/contents [Accessed 25 October 2026].
