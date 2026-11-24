# Final integration check - 24 November 2026

## Current checks

| Check | Observed result |
| --- | --- |
| Python business/integration tests | 45 passed |
| CertificationRegistryTest | 13 passed; no engine or network needed |
| Camunda schema/parser | One validation test passed against all four executable F1/F2 BPMNs |
| F1 route-test compilation | Passed with tests skipped; not a route execution result |
| Existing F2 live evidence | 11 completed version-2 instances; details in the F2 live register |

## Fresh F1 certification request

The UWE Frenchay 2026 environment was Paused when this check began. Resume was requested in Hub; the environment subsequently displayed Healthy and Tasklist/Operate became accessible.

Started `product-listing-publication` version 11 through native Tasklist. Submission task `2251799869051650` belonged to process instance `2251799869051645`, created at 17:19:01 UK time. Synthetic product `TASK1-FINAL-ORGANIC-20261124-1719` used quantity 12, in-season dates 2026-11-01 through 2026-12-31, valid harvest/best-before dates and reference `GB-ORG-05`. Task completion produced listingId `LST-20261124171942254`; productDetailsValid=true and validationErrors=[].

Operate history reached Request certification verification. At inspection it had no certification result, no result-timeout history and no completion. This establishes a pending request, not a healthy certification-worker response. The user reported the worker was running; the runtime evidence does not yet establish it is consuming this request after the environment pause/resume.

The existing F1 service code was incorporated from commit `84a767f7b71373e15cd08773115fc535d8676bff`. A Windows launcher `services/certification-service/start-certification.cmd` reuses the existing credential file, passing credentials only through the child environment. It creates no new credentials and must not be run alongside a competing old certification worker. The user was asked to restart this worker; the same pending instance should continue if connectivity/permissions are correct.

Do not mark verified-organic publication, shared catalogue persistence or the final combined rehearsal complete until that outcome is observed. Historical F1 evidence remains available separately and is not relabelled as a current connected-version run.

