# Camunda Implementation: Functionality 1

| | |
|---|---|
| **Process** | `product-listing-publication` (`camunda/processes/product-listing-publication.bpmn`) |
| **Called process** | `record_product_traceability` (`camunda/processes/record-product-traceability.bpmn`) |
| **Source model** | `models/operational-bpmn/functionality-1/product-listing.bpmn` and `record_product_traceability.bpmn` (Zain-Eldin Sharaf, M3) |
| **Owner** | Omar Fathy (M4) |
| **Backlog** | E1-01 to E1-08 (#30 to #37) |

## 1. From operational model to executable process

The executable process **is Zain's operational model made runnable**. It is a copy of his file with the same pools (Producer, Marketplace, Organic Certification Service), lanes (Marketplace Platform, Marketplace Administrator), data objects, data stores, message flows, layout, element names and gateway variables. His original stays unchanged in `models/` as the operational artefact.

Element IDs were renamed from generated ones (e.g. `Activity_1nu9k0q`) to readable ones (e.g. `Task_CheckOrganicClaim`), so Operate and the tests are easy to follow. This does not change the diagram.

What was added or changed to make it run:

| Operational model element | Executable element | Reason |
|---|---|---|
| Message start "Product details received" (from the Producer pool) | None start "Producer starts listing" and new user task "Submit product details"; the Producer message flow now points at the form | In Camunda the producer works in Tasklist, so the incoming message becomes a form. |
| Message catch "Corrected product details received" | User task "Submit corrected product details" (same place, same message flow) | Same reason: the producer replies through a form. |
| Message catch "Producer decision received" | User task "Decide on rejected organic claim" (same place, same message flow) | Same reason. |
| Send tasks "Request product corrections" and "Notify producer …" | Script tasks that add an entry to `producerNotifications` | Notifications are simulated, and each one is visible in Operate as evidence. The message flows to the Producer pool are kept. |
| Service tasks and the two plain tasks (validation, record, flag, remove claim, withhold, prepare, save, publish) | FEEL script tasks | Internal platform logic runs inside Camunda, so no extra worker is needed. |
| Send task "Request certification verification" | Unchanged, with job type `request-certification-verification` | The only external system call. It is implemented by the simulated certification service (E4-01, M5). |
| Message event "Certification result received" | Unchanged, with message `certification-result` correlated on `listingId` | The service's `certificationStatus` is mapped onto Zain's `certificationVerified` variable. |
| Timers `=PT30S` and `=PT24H` | `PT30S` and `PT24H` | A leading `=` makes Camunda read the value as a FEEL expression, which fails. |
| Call activity `=record_product_traceability` | `record_product_traceability`, with `traceabilityRecord` mapped back | With the `=` the process id was read as a variable name. |
| Sub-processes, event-based gateway, non-interrupting 24 h timer, lanes, data objects and data stores | Unchanged | Data stores are represented by the process variables `catalogueEntry`, `organicStatus` and `traceabilityRecord`; a real database is out of scope for Task 1. |

## 2. Business rules

### Validation (sub-process "Validate product details")

Each script task adds its messages to `validationErrors`. The producer sees every problem at once, not only the first.

| Task | Rule | Message |
|---|---|---|
| Validate mandatory product fields | Producer, name, description, category, price, quantity, origin, allergens, harvest, best-before and season dates are present | "… is required." |
| Validate price and stock quantity | price > 0; quantity ≥ 0 and a whole number | "Price must be greater than zero." / "Quantity cannot be negative." / "Quantity must be a whole number." |
| Validate seasonal availability dates | season end ≥ season start | "Availability end date must be on or after the start date." |
| Validate origin and harvest information | harvest date not in the future | "Harvest date cannot be in the future." |
| Validate allergen and date information | best-before after harvest date and not already passed | "Best-before date must be after the harvest date." / "Best-before date has already passed." |
| Check organic certification details | an organic claim needs a UK control body code (`GB-ORG-nn`) | "A certification reference is required …" / "Certification reference must be a UK organic control body code …" |

The form already blocks a missing field and a price of zero. The cross-field date rules can only be checked by the process. To demo the invalid path, enter a best-before date earlier than the harvest date.

### Routing

The Yes conditions are Zain's, unchanged:

| Gateway | Condition (Zain's) | Default |
|---|---|---|
| Product details valid? | `productDetailsValid = true` → Yes | No → request corrections |
| Organic claim made? | `organicClaimMade = true` → Yes | No → publication |
| Certification verified? | `certificationVerified = true` → Yes | No → rejected-claim path |
| Retry attempts remaining? | `certificationAttempts < 3` → retry | No → manual review |
| Remove organic claim? | `removeOrganicClaim = true` → Yes | No → withhold |
| Organic evidence verified? | `manualCertificationVerified = true` → Yes | No → withhold |

His "No" conditions were turned into default flows, so a missing variable can never leave an instance stuck with an incident.

The forms use text choices, which are reliable in Camunda Forms, and an output mapping turns each one into Zain's true/false variable:
- **Rejected-claim form:** `rejectedClaimDecision = "remove-claim"` → `removeOrganicClaim`.
- **Manual decision form:** `manualReviewDecision = "approve"` → `manualCertificationVerified`.
- **Certification message:** `certificationStatus = "verified"` → `certificationVerified`.

## 3. Variables

| Variable | Type | Set by | Used for |
|---|---|---|---|
| `producerName`, `productName`, `productDescription`, `category` | string | Product form | Product and traceability record |
| `price` | number | Product form | Validation, catalogue |
| `quantity` | integer | Product form | Validation, initial stock (F2) |
| `availableFrom`, `availableUntil` | date string `YYYY-MM-DD` | Product form | Season validation, availability (F2) |
| `origin`, `harvestDate`, `bestBeforeDate`, `allergens` | string | Product form | Traceability record |
| `organicClaimMade` | boolean | Product form; set to `false` by "Remove organic claim" | Routing, catalogue |
| `certificationReference` | string | Product form (shown only for organic claims) | Certification request |
| `validationErrors` | list of strings | Validation sub-process | Correction form |
| `productDetailsValid` | boolean | Validation sub-process | Routing |
| `listingId` | string `LST-…` | Validation sub-process (first run) | Message correlation, records |
| `certificationStatus` | `verified` / `rejected` | Certification service message | Audit |
| `certificationVerified` | boolean | Mapped from `certificationStatus` | Routing |
| `certificationAttempts` | integer | "Record certification timeout" | Retry limit (3) |
| `organicStatus` | string | Record / flag tasks | Catalogue entry |
| `rejectedClaimDecision` | `remove-claim` / `withhold` | Rejected-claim form | Audit |
| `removeOrganicClaim` | boolean | Mapped from `rejectedClaimDecision` | Routing |
| `certificateDocumentSeen`, `evidenceReviewNotes` | boolean, string | Evidence review form | Audit evidence |
| `producerNameMatchesCertificate`, `certificateInDate` | boolean | Producer check form | Audit evidence |
| `manualReviewDecision`, `manualReviewNotes` | `approve` / `reject`, string | Manual review decision form | Audit evidence |
| `manualCertificationVerified` | boolean | Mapped from `manualReviewDecision` | Routing |
| `manualReviewOverdue` | boolean | "Flag manual review as overdue" | Escalation evidence |
| `listingStatus` | `Pending manual review` / `Withheld` / `Published` | Flag, withhold, publish tasks | Outcome |
| `product`, `catalogueEntry` | object | Prepare / save tasks | Simulated catalogue |
| `traceabilityRecord` | object | `record_product_traceability` | Simulated traceability store (E1-07) |
| `producerNotifications` | list of objects | Notify tasks | Simulated notifications (E1-08) |

## 4. Forms

| User task | Form ID | File |
|---|---|---|
| Submit product details | `product-listing-form` | `camunda/forms/product-listing.form` |
| Submit corrected product details | `product-correction-form` | `camunda/forms/product-correction.form` (lists `validationErrors`) |
| Decide on rejected organic claim | `rejected-organic-claim-form` | `camunda/forms/rejected-organic-claim.form` |
| Review submitted certification evidence | `certification-evidence-review-form` | `camunda/forms/certification-evidence-review.form` |
| Check producer and certification details | `producer-certification-check-form` | `camunda/forms/producer-certification-check.form` |
| Record manual review decision | `manual-certification-review-form` | `camunda/forms/manual-certification-review.form` |

## 5. Contract with the simulated certification service (E4-01)

This is the only part of F1 that needs code outside Camunda.

1. **Job:** activate jobs of type `request-certification-verification`. Read `listingId`, `certificationReference` and `producerName`. Complete the job straight away with no variables.
2. **Reply:** publish message `certification-result` with correlation key = `listingId` and variable `certificationStatus` = `"verified"` or `"rejected"`.
3. **Unavailable:** to simulate an outage, complete the job and send no reply. After 30 s the process records a timeout and retries, up to 3 attempts, then sends the listing to manual review.

Suggested demo references, so each result can be triggered on demand:

| Reference | Simulated result |
|---|---|
| `GB-ORG-05` | verified |
| `GB-ORG-99` | rejected |
| `GB-ORG-00` | unavailable (no reply) |

`tests/camunda-f1/src/test/java/uk/ac/uwe/daesd/ProductListingProcessTest.java` plays exactly this role, so it can be used as a reference implementation.
