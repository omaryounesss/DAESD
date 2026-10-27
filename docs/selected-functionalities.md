# Selected Use Case and Major Functionalities

| | |
|---|---|
| **Project** | Online Food Marketplace – UFCFTR-30-3, Assessment Task 1 |
| **Use case** | Use Case 1 – Producer Product Listing and Inventory Management |
| **Authors** | Omar (Member 1), Zain (Member 3) (functionality scoping) |
| **Sprint** | 1 – Strategic Process Analysis and Project Setup |
| **Status** | Agreed |
| **Related artefacts** | `models/strategic-bpmn/strategic-marketplace.bpmn` · `docs/case-study-analysis.md` |

---

## 1. Why we selected Use Case 1

1. **It is the supply side of the enterprise.** Every other business process depends on products being listed accurately. Without listings there is nothing to browse, order or take commission on (see `case-study-analysis.md`, section 5).
2. **It underpins food safety.** Listing captures farm origin, allergens, harvest and best-before dates, and organic claims. The traceability required by the case study, and handled in Use Case 3, depends on this data being correct.
3. **It covers everything the brief asks a functionality to demonstrate:** user interaction, automated processing, business decisions, interaction with an external service, data processing, and alternative and exception flows.
4. **It integrates cleanly into Task 2.** When orders are paid (Use Case 2), stock must go down and products must become unavailable at zero stock. That rule lives in our second functionality, so it is a natural integration point.

## 2. The two candidate major functionalities

Both functionalities appear as collapsed sub-processes in the strategic BPMN, with the same names, and will be expanded into operational BPMN models in Sprint 2.

### Functionality 1: Product listing, validation and publication

**Strategic BPMN element:** *Manage product listings* (Marketplace Platform lane)

| Aspect | Scope |
|---|---|
| Trigger | A registered producer submits a new product. |
| Actors | Producer, Marketplace platform, Organic-certification service. |
| Inputs | Name, description, category, price, quantity, availability period, farm origin, harvest date, allergen details, organic certification, best-before date. |
| Outcome | The product is published and visible to customers, or the producer is asked to correct it. |

**In scope**

- Producer completes and submits the product form.
- Automatic validation of mandatory and invalid fields; the producer corrects and resubmits.
- If organic certification is claimed, a check with an external (simulated) verification service.
- Publication of the validated product to the catalogue.
- Recording of origin, allergen and best-before data for traceability.

**Alternative and exception flows**

- Validation fails → producer asked to correct the details.
- Certification rejected → product cannot be listed as organic.
- Certification service unavailable → retry, then fall back (e.g. manual review or listing without the organic claim). Exact path to be designed in the operational model.

**Out of scope:** payment, ordering, and producer registration (assumed already complete).

### Functionality 2: Inventory and seasonal availability management

**Strategic BPMN element:** *Manage inventory and availability* (Marketplace Platform lane)

| Aspect | Scope |
|---|---|
| Trigger | A producer updates the quantity or seasonal availability of a listed product, or stock changes. |
| Actors | Producer, Marketplace platform. |
| Inputs | Product, new quantity, availability start and end dates. |
| Outcome | The product's availability always reflects its stock and season. |

**In scope**

- Producer updates quantity and seasonal availability.
- Product automatically becomes unavailable for new orders when stock reaches zero.
- Product becomes available again when restocked, if still within its seasonal availability period.

**Alternative and exception flows**

- Restocked but outside the season → product stays unavailable.

**Out of scope:** the ordering process that reduces stock (Use Case 2). We provide the point it connects to.

### Proposed strengthening of Functionality 2

As written in the use case, Functionality 2 is lighter than the brief requires: it has no external service and few exception flows. We propose the following additions, to be agreed with Member 3 and the module team:

| Addition | What it adds |
|---|---|
| Timer events at season start and end | Automatic availability changes without a producer action (automated processing). |
| Low-stock / out-of-stock alert via the notification service | An external service interaction. |
| Rejected updates (e.g. negative quantity, season end before start) returned to the producer | A validation decision and an exception flow. |
| Message start event "order paid – reduce stock" | The integration point with Use Case 2 for Task 2. |

## 3. Coverage against the brief

The brief requires each functionality to give opportunities for the following:

| Requirement | Functionality 1 | Functionality 2 (with proposed additions) |
|---|---|---|
| User interaction | Product form; correcting invalid details | Updating quantity and season |
| Automated processing | Validation; publication | Auto-unavailable at zero stock; timer-based season changes |
| Business decisions | Valid or not? Organic claimed? Certification passed? | Stock at zero? Within season? Update valid? |
| Service interaction | Organic-certification service | Notification service (stock alerts) |
| Data processing | Product, traceability and certification data | Stock levels and availability periods |
| Alternative / exception flows | Invalid details; certification rejected; service unavailable | Restocked out of season; rejected update |

## 4. Traceability

| Strategic BPMN (Sprint 1) | Operational BPMN (Sprint 2) | Camunda (Sprints 2–3) |
|---|---|---|
| *Manage product listings* | Product listing, validation and publication model | Executable listing process with product Form and certification service task |
| *Manage inventory and availability* | Inventory and seasonal availability model | Executable inventory process with timers and stock rules |
| Organic Certification Service pool | Service task with an error path for "service unavailable" | Simulated certification service |

The same names are used at every level so the link from the strategic model to the implementation is visible.

## 5. Agreement

| Item | Status |
|---|---|
| Use Case 1 selected by the group | Agreed |
| Two functionalities as scoped above | Agreed |
| Proposed Functionality 2 additions | Agreed |

The module team's decision will be recorded on a GitHub issue, and this table will be updated.

