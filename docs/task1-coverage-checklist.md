# Current candidate update — 25 November 2026

See [current verification and native rehearsal](task1-verification-2026-11-25.md). This supersedes the older test counts and statements that no payment demonstration exists. The original register below is retained as historical evidence; its human reviews and final native deployment checks are not automatically closed. PR #64 remains the integration candidate.

# Task 1 coverage and evidence checklist

Review version, 24 November 2026. Based on existing recorded checks; preparing this checklist does not run tests again. Complete means the stated evidence exists, not that all production requirements or module marks are guaranteed.

## Assessment coverage

| Requirement | Available evidence | Remaining action or limit |
| --- | --- | --- |
| Both operational processes executed end to end | F1 connected version 11 and F2 version 2; fresh F1-to-F2 catalogue/notification journey | Model authors approve the executable refinements; do not call diagrams identical |
| Forms and user interaction | Six F1 forms; three linked native F2 forms; producer/admin journeys exercised | Full accessibility/user evaluation not completed |
| Service tasks and automation | Validation, certification, traceability, persistence, stock rules, versioned scheduler and outbox | Single-worker classroom setup, not production availability |
| Service/interface/process integration | Actual certification/shared workers; reusable subprocesses; native forms; separate notification receiver | Real checkout/payment/refund and email/SMS not implemented |
| Variables and data flow | Controlled form outputs, listing/update/order IDs, certification correlation, catalogue and receipt records | Identity/producer ownership is not enforced by form/lane grouping |
| Alternatives/exceptions | See route matrix below | Timer and outage evidence must retain its qualifications |
| Relevant users/components/external services | Producer and administrator; certification/notification simulations; paid-order message boundary | Synthetic service outcomes do not establish real certification or human delivery |
| i* -> strategic -> operational -> executable consistency | Traceability and source-content review; source models unchanged | Close C1-C8 in the [consistency review](task1-model-consistency-review.md) |
| Task 2 readiness | Reusable messages, process IDs, product catalogue and service contracts | Agree ownership, stock reservation/payment compensation and authoritative certification |
| LESP | Complete sourced [discussion](task1-lesp-considerations.md) | Members review and explain; resolve permitted-AI questions against the brief |
| Complete/auditable repository | Review PR #64 includes code, forms, models, sources, runbooks and evidence references | Final main candidate, exports, signed contributions and submission commit still need the agreed process |

## Route matrix

| Route/control | Evidence level | Status and qualification |
| --- | --- | --- |
| F1 valid non-organic publication | Earlier connected persistence records and Python integration tests | Recorded; not freshly repeated in the final organic run |
| F1 invalid details -> correction -> revalidation | Historical operational-model version-3 native evidence | Recorded with provenance; not newly repeated on connected version 11 in the final run |
| F1 organic verified | Fresh native version-11 instance 2251799869051645 | Completed; database record confirmed |
| F1 rejected claim -> remove claim | Fresh version-11 instance 2251799869052466 | Completed; published as Not organic |
| F1 rejected claim -> withhold | Fresh version-11 instance 4503599682374083 | Completed; no product persisted |
| F1 unavailable service -> three real timeouts -> manual approval | Fresh version-11 instance 4503599682374333 | Completed with certificationAttempts=3 and synthetic review evidence |
| F1 unavailable service -> three real timeouts -> manual rejection | Fresh version-11 instance 6755399496057319 | Completed Withheld; no product persisted |
| F1 24-hour non-interrupting escalation | XML configuration and inherited embedded test source | NOT freshly observed live. Java compilation is not an execution pass |
| F2 invalid submission -> native correction | Version-2 instance 2251799869042170 | Completed |
| F2 three actual invalid submissions -> administrator allowance -> correction | Version-2 instance 4503599682365771 | Completed; actual invalid attempts recorded |
| F2 administrator rejection | Version-2 instance 2251799869049739 | Completed; deliberately started at review/counter 3, not a new three-attempt journey |
| F2 zero stock -> unavailable and notification | Version-2 instance 6755399496049633 and receiver receipt | Completed; synthetic HTTP receipt, not human delivery |
| F2 outside season; seasonal catch-up; start with zero stock | Version-2 seasonal/update cases in F2 register | Completed; due/missed boundaries tested, not waiting for future midnight |
| F2 duplicate paid order | Instances 2251799869046749 / 2251799869046908 | Completed; distinct message IDs, one business order, no second deduction |
| F2 insufficient stock | Local rollback test and earlier live incidents | Stock remains non-negative; unresolved business compensation is a documented limit |
| F2 48-hour interrupting review timeout | Isolated five-second fixture instance 6755399496053687 | Completed test-only route; assessed PT48H unchanged |
| Full connected F1 -> F2 -> notification | F1 2251799869051645 -> F2 6755399496056666 | Product selected at stock 12, updated to 3, persisted revision 2, receiver low-stock receipt confirmed |
| Recovery after cluster pause | Fresh run paused -> Healthy; user restarted both actual workers | Pending certification/publication resumed and completed. Not a controlled lost-acknowledgement or high-availability test |
| Outbox retry/lost-response/receiver deduplication | Python tests with injected transports and temporary databases | Passed locally; no deliberate live notification-service outage induced |

## Automated checks already recorded

- 45 Python business, scheduling, deployment, layout, notification and integration tests passed.
- 13 certification-registry tests passed.
- One Camunda schema/parser test validated four executable BPMNs.
- Integrated F1/certification Java test sources compiled with route tests skipped. Full embedded execution was blocked by loopback permissions in this session. Their job-based user tasks and publication double are not native Tasklist/SQLite evidence.

## Prioritised remaining checks

| Priority | Action | When |
| --- | --- | --- |
| Before submission | Authors review model refinements, actual AI use and source/export consistency; agree contribution record and module arrangements | Group review |
| Before submission | Rehearse the agreed final main candidate using documented bundles and the shared database; record its commit and deployment versions | After integration approval |
| Useful additional confidence | Fresh connected-version F1 invalid/correction replay; isolated non-interrupting 24-hour escalation fixture or permitted embedded run | If time or assessor expectations justify it; do not relabel historical evidence |
| Useful additional confidence | Controlled live notification outage/recovery and future-boundary schedule test | Isolated environment with explicit test data |
| Before real Task 2 operation | Namespaced certification jobs/invalid-request handling, ownership permissions, payment compensation, real certification and notification channels | Task 2 design/integration |

No new behaviour was added merely to tick a checklist. Unobserved paths remain labelled unobserved. Follow the [merge/submission plan](task1-merge-and-submission-plan.md) and [timed rehearsal](task1-timed-demonstration.md).
