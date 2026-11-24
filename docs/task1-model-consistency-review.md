# Task 1 model consistency review

Prepared 24 November 2026 for group review. No model was edited by this review. Reference main: `5f6395d101463def83dfaa545d1c963f3190186b`; review baseline: `5c34c6cbba54071e83131834e1b18172212cb646`. Later commits add review documents. Findings concern source text/XML and recorded execution, not a new visual inspection of every exported PNG/PDF.

## Method and result

Read the i* SD/SR source files, strategic BPMN XML, both operational BPMN XMLs, current executable BPMNs, traceability and execution registers. Compared Git blob identities for all 23 files under `models/`: main and the review baseline match. The original stakeholder/business models and exports are preserved.

The levels express the same core product-publication and stock/season goals. There are documented execution refinements rather than an exact diagram identity. This is a proposed consistency assessment, not model-author approval or a guarantee that every graphical relation has been formally verified.

| Business concern | i* evidence | Strategic evidence | Operational and executable evidence | Assessment |
| --- | --- | --- | --- | --- |
| Publish accurate products | Product published; Process product listing; Accurate product information | Manage product listings; Product details received | F1 validation subprocess, correction, catalogue/traceability and publication | Core intent aligned; field validation does not establish factual accuracy |
| Verify organic claims | Organic claims verified; Organic claim verified; Trustworthy organic labelling; certification-service dependency | Certification check request/result and external participant | Request/result, retry timer, reject/remove claim or withhold, manual review | Aligned; registry is simulated and human decisions in tests use synthetic fixtures |
| Balance speed and trust | Fast listing and Request manual review | Listing subprocess at strategic level | Three result timeouts then three administrator forms | Detail is appropriately operational; both manual outcomes exercised |
| Keep stock accurate | Stock kept accurate; Up-to-date stock and season data; Read stock and season updates | Manage inventory and availability; Stock and season update | F2 validation, producer forms, save update and correction/admin paths | Aligned subject to native-form refinement below |
| Apply stock/season availability | Availability kept accurate; Make unavailable at zero stock; Check season dates | Stock status updated; inventory subprocess | Zero-stock, within-season and seasonal boundary routes | Outcome aligned; trigger mechanism differs as documented below |
| Warn producers | Send low-stock notification; Notification service dependency | Notification Service participant; inventory detail inside subprocess | Low/zero-stock send jobs, durable outbox, separate simulated receipts | Interaction implemented; human email/SMS receipt is not claimed |
| Reduce stock for paid orders | Reduce stock by purchased quantity | Process orders and payments writes Product catalogue | Paid-order message and deduction, duplicate business-order protection | Integration boundary aligned; compensation for insufficient stock unresolved |
| Provide customer value | Customer dependencies for accurate product/allergen/origin information and honest claims | Customer, browse/order and quality-incident interactions | F1/F2 supply accurate catalogue/availability data for downstream use | Customer need is represented; a new customer task inside these two supply-side processes is not necessary |

## Executable comparisons

F2's 56 original sequence flows retain their IDs and source/target endpoints. The executable adds a producer none start, catalogue preparation and submission route; the original correction event becomes a native user task. The obsolete incoming correction message and its DI edge are removed. These changes retain original validation/review/availability branches; the tests check those relationships, not author intent.

F1 retains every original named task/subprocess/gateway when script tasks and repeated names are included in the comparison, and adds three named form interactions: Submit product details, Submit corrected product details and Decide on rejected organic claim. F1 uses new readable IDs, so none of the 56 original flow IDs supplies a direct endpoint comparison. Matching names and successful routes do not by themselves prove complete graph equivalence. Zain and Omar Fathy should check the F1 source/executable side by side, particularly nesting, gateway defaults and the non-interrupting manual-review branch.

## Review decisions and discrepancies

| ID | Finding | Proposed resolution | Reviewer |
| --- | --- | --- | --- |
| C1 | Operational producer message interactions become native form tasks in F1/F2 | Retain the native tasks as the executable interface refinement. Explain it in traceability; do not claim the diagrams are identical | M3 + M4 |
| C2 | Operational F2 seasonal timers become messages from the persistent per-product scheduler | Retain message starts to avoid fixed deployment dates. Verify due dates, versions and inclusive end semantics against the source's business intent | M3 + M4 |
| C3 | Marketplace operations contains producer forms and automated tasks; Tasklist lane was removed | Treat lane as process grouping, not identity/access enforcement. Keep administrator review distinct | M3 + M4 |
| C4 | Main's earlier traceability/F2 planned wording and selected-functionality future-tense passages lag execution | Use the review branch's current supplement. Revise historical scoping text only with its authors; reference the agreed timed-retry/manual-review fallback rather than ambiguous alternatives | M1 + M3 + M4 |
| C5 | Role/scoping documents record group agreement, but a module-team approval reference is not established by the reviewed material | Add the actual module-team issue/email/meeting reference when available; do not infer it from the group's Agreed status | M1 |
| C6 | F1 service consumes a generic request-certification-verification job type; restart logs included requests with null listing/producer/reference | Review namespacing and invalid-request handling before broader Task 2 use. Our listing's verified result is independently confirmed; do not assume null requests belong to this group | M4 + M5 |
| C7 | F1 manual-review 24-hour escalation has not been freshly observed live | Keep it explicit in coverage. If more evidence is required, use an isolated non-interrupting accelerated fixture or a permitted embedded engine, without altering the assessed duration | M3 + M4 + M5 |
| C8 | AI assistance includes executable model refinements/layout as well as code/docs | Check the assessment's permitted-use wording against actual assistance and obtain module clarification if needed. Source preservation and group review are not substitutes for meeting the requirement | All members |

No additional confirmed missing core task was found in this source review. This conclusion does not close the decisions above or certify every strategic/i* graphical link.

## Proposed review record

For each C-item record the reviewer's name, date, accept/change decision, reason and any issue/commit. Do not prefill approval or signatures. Check the corresponding PNG/PDF export if any source model is changed. Evidence: [traceability](traceability.md), [F2 mapping](f2-tasklist-refinement.md), [live check](task1-final-live-check-2026-11-24.md).

