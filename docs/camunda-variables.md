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