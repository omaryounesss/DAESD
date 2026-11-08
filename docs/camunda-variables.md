# Camunda Implementation: Functionality 1

| | |
|---|---|
| **Process** | `product-listing-publication` (`camunda/processes/product-listing-publication.bpmn`) |
| **Called process** | `record-product-traceability` (`camunda/processes/record-product-traceability.bpmn`) |
| **Source model** | `models/operational-bpmn/functionality-1/product-listing.bpmn` (Zain-Eldin Sharaf, M3) |
| **Owner** | Omar Fathy (M4) |
| **Backlog** | E1-01 to E1-08 (#30 to #37) |

## 1. From operational model to executable process

Element names are the same as in the operational model. Where an element had to change type to run in Camunda 8, the table below says why.

| Operational model element | Executable element | Reason |
|---|---|---|
| Message start "Product details received" | None start "Producer starts listing" and user task "Submit product details" | The producer is a separate pool in the operational model. In Camunda the producer works in Tasklist, so the message becomes a form. |
| Send task "Request product corrections" and message catch "Corrected product details received" | Script task "Request product corrections" and user task "Submit corrected product details" | Same reason: the producer replies through a form. |
| Send task "Notify producer of rejected claim" and message catch "Producer decision received" | Script task "Notify producer of rejected claim" and user task "Decide on rejected organic claim" | Same reason. |
| Send tasks "Notify producer …" | Script tasks that add an entry to `producerNotifications` | Notifications are simulated, and each one is visible in Operate as evidence. |
| Service tasks (validation, record, flag, prepare, save, publish) | FEEL script tasks | Internal platform logic runs inside Camunda, so no extra worker is needed. |
| Send task "Request certification verification" | Send task with job type `request-certification-verification` | This is the only external system call. It is implemented by the simulated certification service (E4-01, M5). |
| Event-based gateway, message "Certification result received", timer "Certification response timeout" (30 s) | Unchanged | Message `certification-result`, correlated on `listingId`. |
| Sub-processes "Validate product details" and "Manually review certification" | Unchanged (collapsed, drill down in Modeler) | |
| Non-interrupting timer "Manual review deadline exceeded" (24 h) | Unchanged | |
| Call activity "Record product traceability" | Unchanged; calls `record-product-traceability` | |
| Data stores (Product Catalogue, Certification Records, Traceability Records) | Process variables `catalogueEntry`, `organicStatus`, `traceabilityRecord` | A real database is out of scope for Task 1. |

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

| Gateway | Condition | Default |
|---|---|---|
| Product details valid? | `productDetailsValid = true` → Yes | No → request corrections |
| Organic claim made? | `organicClaimMade = true` → Yes | No → publication |
| Certification verified? | `certificationStatus = "verified"` → Yes | No → rejected-claim path |
| Retry attempts remaining? | `certificationAttempts < 3` → retry | No → manual review |
| Remove organic claim? | `rejectedClaimDecision = "remove-claim"` → Yes | No → withhold |
| Organic evidence verified? | `manualReviewDecision = "approve"` → Yes | No → withhold |

Every gateway has a default flow, so a missing variable can never leave an instance stuck with an incident.

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
| `certificationStatus` | `verified` / `rejected` | Certification service message | Routing |
| `certificationAttempts` | integer | "Record certification timeout" | Retry limit (3) |
| `organicStatus` | string | Record / flag tasks | Catalogue entry |
| `rejectedClaimDecision` | `remove-claim` / `withhold` | Rejected-claim form | Routing |
| `certificateDocumentSeen`, `evidenceReviewNotes` | boolean, string | Evidence review form | Audit evidence |
| `producerNameMatchesCertificate`, `certificateInDate` | boolean | Producer check form | Audit evidence |
| `manualReviewDecision`, `manualReviewNotes` | `approve` / `reject`, string | Manual review decision form | Routing, audit evidence |
| `manualReviewOverdue` | boolean | "Flag manual review as overdue" | Escalation evidence |
| `listingStatus` | `Pending manual review` / `Withheld` / `Published` | Flag, withhold, publish tasks | Outcome |
| `product`, `catalogueEntry` | object | Prepare / save tasks | Simulated catalogue |
| `traceabilityRecord` | object | `record-product-traceability` | Simulated traceability store (E1-07) |
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
