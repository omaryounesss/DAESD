# Simulated Organic-Certification Service (E4-01)

Owner: Mohamed Hamdy (M5). Backlog item E4-01 (#51), used by E1-04 (#33) and E1-05 (#34).

A stand-in for a real UK organic control body. It answers the service task **Request certification verification** in Functionality 1 (`camunda/processes/product-listing-publication.bpmn`), following the contract in [docs/camunda-variables.md §5](../../docs/camunda-variables.md).

## How it works

```
Camunda F1 process                          Certification service
──────────────────                          ─────────────────────
Request certification verification  ──job──▶  1. read listingId, certificationReference, producerName
                                    ◀─done──  2. complete the job straight away
Wait for certification result       ◀──msg──  3. publish "certification-result"
  (30 s timeout, up to 3 attempts)               correlation key = listingId
                                                 certificationStatus = "verified" | "rejected"
                                                 (no message = service unavailable)
```

| Reference | Answer | What the process does |
|---|---|---|
| `GB-ORG-00` | no reply (unavailable) | Times out after 30 s, retries, then sends the listing to administrator review |
| `GB-ORG-99` | `rejected` | Producer removes the organic claim or withholds the listing |
| any other `GB-ORG-nn` | `verified` | Product published as organic |
| anything else | `rejected` | (the process already blocks wrong formats at validation) |

## Files

| File | What it does |
|---|---|
| `CertificationRegistry.java` | Decides the answer for a reference (the table above) |
| `CertificationResult.java` | The three possible answers |
| `CertificationJobHandler.java` | Takes the Camunda job, completes it, then sends the reply message |
| `CertificationServiceApp.java` | Starts the job worker and connects to Camunda |

## Requirements

Java 21+ and Maven (the same as `tests/camunda-f1`). On a Mac: `brew install openjdk@21 maven`.

## Run the tests

```
cd services/certification-service
mvn test
```

- `CertificationRegistryTest`: unit tests for every reference rule.
- `CertificationServiceProcessTest`: runs the real F1 process from `camunda/` on an embedded Zeebe engine, with this service answering. It covers the verified, rejected and unavailable (3 timeouts, then manual review) routes.

## Run the service

**Local Camunda 8 Run** (see `camunda/README.md`): start Camunda, deploy the F1 files, then:

```
cd services/certification-service
mvn compile exec:java
```

It connects to `localhost:26500`. Change this with `ZEEBE_ADDRESS`.

**Camunda 8 SaaS**: create an API client for the cluster, then set these before `mvn compile exec:java`:

```
export CAMUNDA_CLUSTER_ID=...
export CAMUNDA_CLUSTER_REGION=...
export ZEEBE_CLIENT_ID=...
export ZEEBE_CLIENT_SECRET=...
```

`REPLY_DELAY_SECONDS` (default 2) sets how long the "external service" takes to answer, so the wait is visible in Operate.

## Demo

With the service running, start F1 in Tasklist and tick "organic":

1. `GB-ORG-05` → the listing is published as organic.
2. `GB-ORG-99` → the rejected-claim decision form appears.
3. `GB-ORG-00` → wait about 90 seconds → three administrator review tasks appear.

The service logs every request and reply in the terminal.
