# Camunda variables — Functionality 1

This is the executable implementation of Zain's operational model at `models/operational-bpmn/functionality-1/product-listing.bpmn`.

| Variable | Type | Produced by | Used for |
|---|---|---|---|
| `productName`, `productDescription`, `category` | string | Producer form | Product record |
| `price` | number | Producer form | Validation and catalogue record |
| `quantity` | number | Producer form | Validation and initial inventory |
| `origin`, `harvestDate`, `bestBeforeDate`, `allergens` | string | Producer form | Traceability record |
| `organicClaimMade` | boolean | Producer form / check worker | Routes organic and non-organic listings |
| `certificationReference` | string | Producer form | Certification verification request |
| `productDetailsValid` | boolean | `validate-product-listing` worker | Valid / correction route |
| `validationErrors` | string array | `validate-product-listing` worker | Shown when the producer corrects details |
| `certificationStatus` | string | Certification service | `verified`, `rejected`, or `unavailable` |
| `certificationAttempts` | number | Certification workers | Maximum three verification requests |
| `manualCertificationVerified` | boolean | Administrator review form | Manual-review route |
| `manualReviewNotes` | string | Administrator review form | Audit evidence |
| `removeOrganicClaim` | boolean | Producer decision form | Continue without claim or withhold |
| `listingStatus` | string | Catalogue/publication workers | `Published` or `Withheld` |

## Job-worker contracts

The BPMN uses Camunda job types so that the process can be deployed now and connected to the simulated services in Sprint 2/3:

- `validate-product-listing`: sets `productDetailsValid` and `validationErrors`.
- `request-certification-verification`: increments `certificationAttempts` and sets `certificationStatus`.
- `record-certification-timeout`: preserves the attempt count after an unavailable response.
- Catalogue/publication/notification job types: persist the product, status and producer outcome.

For the first demo, Mohamed Ahmed's simulated certification service should return each of the three `certificationStatus` values on demand.


## Form mapping

| BPMN user task | Form ID | Purpose |
|---|---|---|
| Submit product details | `product-listing-form` | Capture the initial listing and traceability data. |
| Correct product details | `product-correction-form` | Amend invalid data and resubmit using the same process variables. |
| Decide how to proceed after rejected claim | `rejected-organic-claim-form` | Allow the producer to remove the organic claim or withhold the listing. |
| Manually review certification | `manual-certification-review-form` | Record the administrator’s evidence-based decision. |

## Full service-task contract

| Job type | Required input | Required output / effect |
|---|---|---|
| `validate-product-listing` | Product and traceability variables | Sets `productDetailsValid` and `validationErrors`. |
| `check-organic-claim` | `organicClaimMade` | Normalises the claim variable before routing. |
| `request-certification-verification` | `certificationReference`, product data, `certificationAttempts` | Increments attempts and sets `certificationStatus` to `verified`, `rejected`, or `unavailable`. |
| `record-certification-timeout` | `certificationStatus`, `certificationAttempts` | Records an unavailable response before retry/manual review. |
| `record-verified-organic-status` / `record-manual-certification` | Certification decision | Stores verified certification evidence for publication. |
| `flag-rejected-organic-claim` / `remove-organic-claim` | Certification status / producer decision | Prevents a rejected claim from being published as organic. |
| `withhold-product-listing` | Product and decision data | Sets `listingStatus` to `Withheld`. |
| `prepare-publication` / `save-product-to-catalogue` / `publish-product-listing` | Approved listing data | Persists the traceability data and sets `listingStatus` to `Published`. |
| `notify-producer-published` / `notify-producer-withheld` | Producer and listing status | Sends the final outcome notification. |

**Integration boundary:** Mohamed Ahmed (M5) supplies the simulated certification worker and shared end-to-end test evidence. This branch defines the Camunda job types, variables and process routes that those workers must satisfy.
