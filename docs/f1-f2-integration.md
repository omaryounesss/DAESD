> Current F2 status: the Tasklist, message-scheduler and notification-service refinements supersede older F2 instructions in this historical review. Use [the current runbook](../camunda/f2/README.md) and [version-2 live evidence](f2-tasklist-live-validation-2026-11-24.md).

# F1 to F2 catalogue integration

Current evidence update, 24 November: the catalogue now contains F1-published products. Live F2 update `omar-update-003` completed at quantity 40 and order `omar-order-008` completed at quantity 37 for the same product; Operate and SQLite agree. See [completion review](task1-completion-review-2026-11-24.md). The original installation/verification limitations below describe the earlier installation session, not a claim that integration is still undeployed.

F1's existing "Publish product listing" task is now a service task with job type
f1-publish-product. The inventory worker handles it using the same SQLite database
as F2. It commits the product, traceability, season schedule and cached job result
in one transaction before completing the job. F1 then notifies the producer.

The existing operational diagrams and F2 routes are unchanged. F1 forms, certification
and manual-review routes are preserved. A failed database write prevents F1 from
reporting successful publication. Retry does not reset stock already changed by F2.
A different listing cannot replace an existing product with the same ID.

## Install and activate

1. Stop the inventory worker with Ctrl+C.
2. Extract this zip. In PowerShell run the extracted INSTALL.ps1:
   & "C:\path\to\extracted\INSTALL.ps1"
   The installer backs up the existing worker and existing camunda/f1 directory.
   It does not replace or delete the catalogue database.
3. Restart the existing services/inventory-service/start-f2.cmd.
4. Run:
   python "C:\Users\omarf\Documents\Projects\DaESD\f2-work\scripts\deploy_f1.py"
   This reads your existing cluster credential file without printing or saving secrets.
   Alternatively upload all files in camunda/f1/forms and camunda/f1/processes
   to Web Modeler and deploy together.
5. Start a NEW F1 instance and complete its product form. An organic product
   still needs the existing certification service or the manual review route.
6. After publication, Operate shows productId and cataloguePersisted=true.
   Copy that exact productId into f2-stock-update.

By default productId equals F1's generated listingId (LST-...). To create P2
specifically, start the F1 instance with {"productId":"P2"}, then complete the form.
P2 must not already belong to another listing or a seeded demo product.

The existing waiting P2 update can resume with f2-stock-corrected,
correlationKey omar-update-001, once P2 has been published by the connected F1.
Existing F1 instances stay on their original deployed version and do not gain this integration.

## Verification

Python integration tests cover publication, database reopen, F2 validation,
stock update and purchase, duplicate delivery, collision rejection and invalid
publication rollback. The existing F2 test suite is also run.
The F1 embedded engine route tests use a simulated publication worker; actual
SQLite effects are tested by Python. Live cluster verification is separate.

## Current limitation

This is a local demo catalogue: keep one shared worker running against the same
database. It is not a centrally hosted catalogue service.

Verification on 24 November 2026: 32 Python tests passed. The 11 embedded
Camunda route tests compiled, but could not start their engine because this
session blocks loopback sockets (Permission denied: connect). They must be
rerun outside this restricted session. No live deployment or live F1/F2 test
has been performed. The running project has not been changed.

