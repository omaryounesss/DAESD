# Task 1 completion candidate â€” 25 November 2026

This update preserves the group-authored i*, strategic and operational models. It extends the executable F2 duplicate with customer ordering and simulated payment. Main is unchanged; the candidate is in PR #64.

## Changes made

- The horizontal ordering diagram, its forms, payment simulation, worker handlers and rebuild scripts are now version controlled together.
- Ordering deployment includes the stock-check child process and all six F2 forms. It no longer assumes those dependencies were previously deployed.
- Only `place-order-horizontal.bpmn` is deployed for process ID `f2_customer_ordering`. `place-order.bpmn` is an identical compatibility copy; never deploy both in one bundle.
- Five embedded ordering tests cover successful low-stock purchase, last-item purchase, declined payment, insufficient stock and voiding authorization after a stock race.
- CI runs the Python suite, F1 routes, F2 routes/schema validation and certification registry/integration on Linux with Java 21. Reports are retained as workflow artifacts.
- The embedded F1 publication double now returns `listingStatus=Published`, matching the real shared worker. The F2 test deployment excludes the ordering compatibility copy. These fix failures exposed by the first CI run without weakening assertions.
- `scripts/verify_ordering_live.py` provides a repeatable native-task rehearsal using a new synthetic product each time. It checks stock, completed instances, simulated payment receipts and independent low/zero-stock notification receipts. It does not start a worker or reuse the earlier incomplete instance.

## Evidence distinctions

55 Python tests pass locally. The Java sources compile. Current CI results must be read from the linked workflow for the exact candidate commit; compiling is not an engine-test pass.

Embedded process tests use job-based substitutes for native user tasks and explicit service results. The certification integration suite uses the actual certification handler. Python tests exercise real SQLite business transactions and receipt stores with injected transports. These layers complement the historical native execution register; they do not establish that the latest deployment has completed a native Tasklist journey.

The earlier live ordering instance `2251799869186232` remains incomplete evidence. No successful checkout is inferred from deployment success, message acceptance or passing local tests.

## Final native rehearsal

From the candidate repository root on the demonstration computer:

1. Stop the older inventory worker. Keep only one shared worker using the existing catalogue. Do not replace the database with a test copy.
2. Deploy `python scripts/deploy_f1.py`, `python scripts/deploy_f2.py`, then `python scripts/deploy_ordering.py` using the existing configured credentials.
3. In one terminal run `python services/inventory-service/connect_f2.py --credentials "$HOME/Downloads/daesd-omar-f2-worker-springboot.properties"`. It starts the two local simulations and shared worker.
4. In another terminal start the certification worker with `python services/certification-service/start-certification.py` when demonstrating organic F1 routes.
5. Run `python scripts/verify_ordering_live.py --credentials "$HOME/Downloads/daesd-omar-f2-worker-springboot.properties"`. Its report is `docs/ordering-live-verification.json`; only a report with status `PASS` closes this ordering check.
6. Rehearse F1 publication followed by native F2 stock update using the same catalogue. Record the candidate commit and deployed definition versions. Retain the earlier qualified evidence for retries, correction, review and seasonal routes.

The ordering rehearsal creates only uniquely named synthetic stock and simulated payments. It expects stock `4 -> 1 -> 1 -> 1 -> 0`, two captures, one decline, no payment for the invalid order, and both low-stock and out-of-stock receipts. Test data and process instances are retained for inspection. Inspect a failure before retrying; each invocation creates new IDs.

## Remaining completion conditions

The final native rehearsal, model-author review, actual module-team scope agreement, individually signed contribution matrix, individual Q&A rehearsal and final maintainer-approved integration/submission remain separate conditions. Do not sign, claim approval or certify authorship for another member. No new authorization to merge main is implied by this candidate.

The classroom payment and notification services are simulations. Real checkout, email/SMS, authenticated product ownership and production availability are not claimed.
