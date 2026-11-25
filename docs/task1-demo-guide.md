# Task 1 demonstration and handover

Prepared 24 November 2026. This is a rehearsal guide, not a new test result or group sign-off. Deadline: before 14:00 UK time, 10 December 2026. Use the group repository, live demonstration and individual Q&A; a separate report/video is not required by the supplied brief.

## Start here

1. Confirm the UWE Frenchay 2026 environment is Healthy in Camunda Hub. A paused/resuming cluster cannot establish that a worker is connected.
2. Keep the existing shared inventory worker running with its existing database. If it has stopped, run `services/inventory-service/start-f2.cmd` from the checkout. It reads the existing credentials file in Downloads; do not put credentials in Git or screenshots. It starts the separate local notification simulation if necessary.
3. Confirm Mohamed's certification service is running against this same cluster. Its console starting is insufficient: use the verified-organic scenario below to observe a request and result. The existing Java source and registry rules are included under `services/certification-service`; no new worker should compete with his running worker.
4. Deploy the connected F1 bundle (two processes and six forms) and F2 bundle (two processes and three forms) together within each functionality. F2 uses deployment-bound forms: do not deploy its main BPMN on its own. Do not redeploy old fixed-date F2 files. Existing instances retain their version.
5. Use Tasklist for producer/admin forms and Operate for token history, variables, completion and incidents. API message acceptance alone is not proof of completion.

## Main demonstration

Use synthetic data and a unique product name, for example `TASK1-DEMO-<date-time>`. Use an in-season range, positive total quantity and valid harvest/best-before dates.

| Step | Action | What to show |
| --- | --- | --- |
| F1 publication | Start the connected `product-listing-publication`, submit a valid non-organic product | Publication completes; productId/listingId and cataloguePersisted=true; matching SQLite product and traceability |
| F2 producer update | Start `Process_0g8kz9d` from its none start; select the product in the form | Product is offered from the shared catalogue; validated quantity and inclusive season dates persist |
| Correction | Submit an invalid date order; then fix it in the correction form | All validation errors visible; original updateId retained; counter is not a producer-editable field; revalidation succeeds |
| Low and zero stock | Set a positive quantity below its lowStockThreshold, then zero in separate form updates | Correct availability branches and separate simulated notification receipts; zero remains unavailable |
| Seasonal behaviour | Open the recorded per-product seasonal instances and schedule evidence | Messages, version check, cancelled superseded dates, inclusive end boundary and no past-date fixed timer |
| Order integration | Use the existing paid-order message contract with synthetic IDs | Successful deduction once; repeat the business order with a distinct message ID and show no second deduction |

For each new run record process version, instance key, update/order ID, before/after quantity, end state and receipt ID. Keep the stock in a sensible state after demonstration; do not erase audit history.

## F1 certification scenarios

| Input | Expected behaviour |
| --- | --- |
| Organic `GB-ORG-05` | Service acknowledges the request and sends certification-result, correlated by listingId; published as verified organic and persisted |
| Organic `GB-ORG-99`, remove claim | Rejected-claim form; publish as non-organic |
| Organic `GB-ORG-99`, keep claim | Withheld; no newly published catalogue product |
| Organic `GB-ORG-00` | Service acknowledges but sends no result. Three 30-second result timeouts lead to administrator evidence, producer-check and decision forms |
| Administrator approves/rejects | Publish only when evidence is accepted; otherwise withhold |

If the token stays at Request certification verification, the request worker is not completing jobs. This is different from the intended outage simulation, which completes the job and waits at the message/timer gateway. Historical F1 version-3 evidence is indexed in [the correction/provenance note](f1-testing-correction.md); it is not a new run of the connected version.

## Exceptions and evidence

F2's live register records 11 completed version-2 instances, native correction/admin branches, seasonal catch-up, zero stock and a duplicate business order. The 48-hour review timeout was exercised using an isolated five-second test-only clone; the assessed BPMN remains PT48H. Do not describe that as waiting 48 hours in production.

Insufficient stock currently raises an incident and preserves non-negative stock. It does not refund a payment or emit the ordinary zero-stock notification. The payment provider is a simulated integration boundary. Notifications are local HTTP simulation receipts, not emails/SMS. This classroom implementation does not enforce producer product ownership or offer production high availability.

## Repeatable local checks

From the repository root:

```powershell
python -m unittest discover -s tests
Push-Location tests/camunda-f2
mvn -o '-Dtest=ModelValidationTest' test
Pop-Location
Push-Location services/certification-service
mvn -o '-Dtest=CertificationRegistryTest' test
Pop-Location
```

Offline mode requires dependencies already cached. The full embedded process tests require permitted loopback sockets; a startup permission failure is an environment limitation, not a passing route test. Native UI journeys remain separate evidence. Java route tests substitute job-based user tasks and a publication-job double; they do not prove native Tasklist or SQLite writes.

## Individual explanation prompts

- Why this work implements the two selected functionalities, and how each traces to i* and the strategic/operational models.
- Why an operational message interaction becomes a native form task in execution; a lane is optional grouping, not access control.
- How validation, correction attempts, administrator decisions and interrupting/non-interrupting timers differ between F1 and F2.
- Why SQLite is suitable for this single-worker classroom demonstration; how transactions prevent partial writes.
- Why jobs/order IDs prevent repeated side effects and why message IDs alone do not identify a business order.
- Why the outbox commits delivery intent with the business event; why committed, sent and receiver-accepted are different states.
- Why seasonal messages carry product and version, and why an end date is inclusive.
- What remains a limitation: paid-order oversell compensation, product ownership, real notification channels and availability at production scale.

## Legal, ethical, social and professional considerations

The complete [LESP review document](task1-lesp-considerations.md) explains the legal sources, implementation choices, stakeholder impacts, authorship/evidence responsibilities and Task 2 actions. For the demonstration, explain the link between each safeguard and the harm it reduces: accurate claims, protected information, usable corrections, fair outage handling and auditable decisions. Distinguish existing safeguards from future work and simulated outcomes from real certification or delivery.

## Group-only completion

Confirm selected functionalities with the module team, approve model consistency and the review branch, agree merge order, sign the contribution matrix individually, confirm the live demo arrangement and rehearse each member's Q&A. These are not completed by preparing this document.

