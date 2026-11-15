# Evidence: Functionality 1 on Camunda (UWE Frenchay 2026)

Screenshots from the university environment **UWE Frenchay 2026** (Camunda 8.9, region `lhr-1`), taken on 15 November 2026. Process `product-listing-publication`, version 3, with the simulated certification service (E4-01, Mohamed Hamdy) running.

Owner: Omar Abdelaaty (M4). Backlog: E1-01 to E1-08 (#30–#37), E4-01 (#51).

## Routes (Operate)

| File | Route | Instance key | Outcome |
|---|---|---|---|
| [F1-1-valid-non-organic.png](F1-1-valid-non-organic.png) | Valid, non-organic | 2251799867429824 | Published |
| [F1-2-invalid-then-corrected.png](F1-2-invalid-then-corrected.png) | Invalid details, corrected and revalidated (execution count 2) | 4503599681090319 | Published |
| [F1-3-organic-verified.png](F1-3-organic-verified.png) | Organic claim verified by the certification service (`GB-ORG-05`) | 4503599681090494 | Published, Verified organic |
| [F1-4-organic-rejected-claim-removed.png](F1-4-organic-rejected-claim-removed.png) | Organic claim rejected (`GB-ORG-99`), producer removed the claim | 6755399494773083 | Published as non-organic |
| [F1-5-organic-rejected-withheld.png](F1-5-organic-rejected-withheld.png) | Organic claim rejected (`GB-ORG-99`), producer withheld the listing | 6755399494773276 | Listing withheld |
| [F1-6-unavailable-manual-review.png](F1-6-unavailable-manual-review.png) | Service unavailable (`GB-ORG-00`): 3 timeouts, then Administrator manual review approved | 2251799867430006 | Published, Verified organic (manual review) |

## Waiting for the producer (Operate)

| File | Shows |
|---|---|
| [F1-7-waiting-at-correction-form.png](F1-7-waiting-at-correction-form.png) | Listing paused at "Submit corrected product details" |
| [F1-8-waiting-at-rejected-claim-decision.png](F1-8-waiting-at-rejected-claim-decision.png) | Listing paused at "Decide on rejected organic claim" |

## Forms (Tasklist)

| File | Shows |
|---|---|
| [F1-9-tasklist-correction-form.png](F1-9-tasklist-correction-form.png) | Correction form listing every validation error, with the earlier answers filled in |
| [F1-10-tasklist-rejected-claim-form.png](F1-10-tasklist-rejected-claim-form.png) | Rejected-claim decision form |

The same routes are also covered by the automated tests in `tests/camunda-f1` (11 tests) and `services/certification-service` (17 tests).
