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

Initially, Operate history stopped at Request certification verification, with no result, result-timeout history or completion. This was recorded as a pending request rather than proof of a healthy worker. The recovery and successful outcomes below supersede that initial state.

The existing F1 service code was incorporated from commit `84a767f7b71373e15cd08773115fc535d8676bff`. A Windows launcher `services/certification-service/start-certification.cmd` reuses the existing credential file, passing credentials only through the child environment. It creates no new credentials and must not be run alongside a competing old certification worker. The user was asked to restart this worker; the same pending instance should continue if connectivity/permissions are correct.

## Recovery and completed connected checks

The user restarted the certification worker at 17:22:23. Its log showed our listing `LST-20261124171942254` checked as VERIFIED and a `verified` response at 17:22:26. Operate independently showed certificationStatus=verified, certificationVerified=true and the traceability call. The shared worker then needed restarting after the cluster pause; it logged successful publication and seasonal jobs. The original F1 version-11 instance completed at 17:23:43 with cataloguePersisted=true and the published end event.

| Scenario | Instance/task | Evidence |
| --- | --- | --- |
| Verified organic | F1 instance `2251799869051645`, submission task `2251799869051650` | Completed; product `LST-20261124171942254` persisted with verified organic status |
| Rejected claim, remove claim | F1 instance `2251799869052466`, submission task `2251799869052471`, producer decision task `2251799869052705` | Completed 17:24:31; product `LST-20261124172358452` persisted as Not organic |
| Rejected claim, withhold | F1 instance `4503599682374083`, submission task `4503599682374088`, decision task `4503599682374290` | Completed 17:25:24; no TASK1-FINAL-REJECT-WITHHOLD product in the shared catalogue |
| Three real timeouts, manual approval | F1 instance `4503599682374333`, submission task `4503599682374338`; manual tasks `4503599682375272`, `4503599682375574`, `4503599682375699` | Completed 17:27:58. Operate history showed three Certification response timeout events, certificationAttempts=3 and manual review. Synthetic fixture notes explicitly excluded any real certificate determination. Product `LST-20261124172519709` persisted as Verified organic (manual review) |
| Same organic product through F2 | F2 instance `6755399496056666`, submission task `6755399496056683` | Completed 17:25:51. Native dropdown offered the exact F1 product at stock 12. Native form set total stock 3; SQLite showed revision 2, available=true |
| Separate notification acceptance | Receipt `notification:LST-20261124171942254:2:low-stock` | Read-only inspection of the independent receiver database confirmed productId, quantity=3 and type=low-stock. Shared outbox had zero pending entries at inspection |
| Three real timeouts, manual rejection | F1 instance `6755399496057319`, submission task `6755399496057324`; manual tasks `6755399496058200`, `6755399496058380`, `6755399496058498` | Completed 17:29:33. certificationAttempts=3, evidence checks false, manualReviewDecision=reject, manualCertificationVerified=false, listingStatus=Withheld and Listing withheld end event. Listing `LST-20261124172708614` was not published |

The certification worker, shared SQLite worker and separate notification service were exercised together after recovery. Historical F1 evidence remains separately identified; these are fresh connected-version checks. No real certificate was verified: all approval/rejection data explicitly represented synthetic classroom fixtures.

The F1 non-interrupting 24-hour escalation was not newly waited out in this run. Its configuration and inherited test source are present; do not present compilation or previous results as a new live escalation test. The separate F2 PT48H timeout remains supported by its explicitly isolated accelerated fixture.

