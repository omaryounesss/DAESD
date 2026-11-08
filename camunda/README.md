# Camunda 8 Processes and Forms

Executable processes for Use Case 1. Owner: Omar Fathy (M4).

```
camunda/
├── processes/
│   ├── product-listing-publication.bpmn   F1: product listing, validation and publication
│   └── record-product-traceability.bpmn   Called by F1 to store traceability data
└── forms/                                 Camunda Forms used by the user tasks
```

Design notes, business rules, variables and the certification-service contract: [docs/camunda-variables.md](../docs/camunda-variables.md).

## Deploying to Camunda 8 SaaS

1. Open the project in Web Modeler, or open the files in Camunda Desktop Modeler.
2. Deploy **all six forms first**, then `record-product-traceability.bpmn`, then `product-listing-publication.bpmn`. The user tasks link to forms by ID, and the call activity links to the traceability process by ID, so these must already exist on the cluster.
3. Start `product-listing-publication` from Modeler ("Run") or from Tasklist ("Processes").
4. Complete the user tasks in **Tasklist** and follow the instance in **Operate**.

## Demo script (one instance per route)

| Route | What to enter | Expected end |
|---|---|---|
| Valid, non-organic | Valid dates, organic unticked | Product listing published successfully |
| Invalid, then corrected | Best-before date earlier than harvest date | Correction form lists the errors; after fixing → published |
| Organic, verified | Organic ticked, `GB-ORG-05` | Published, `organicStatus = Verified organic` |
| Organic, rejected → remove claim | `GB-ORG-99`, choose "Remove the organic claim" | Published as non-organic |
| Organic, rejected → withhold | `GB-ORG-99`, choose "Withhold this listing" | Listing withheld |
| Service unavailable → manual review | `GB-ORG-00`, wait about 90 s (3 timeouts) | Three review tasks in Tasklist; approve → published, reject → withheld |

The organic routes need the simulated certification service (E4-01) to be running against the cluster. Without it, an organic listing waits at "Request certification verification".

## Automated tests

`tests/camunda-f1` runs every route above on an embedded Zeebe engine (no cluster or Docker needed):

```
cd tests/camunda-f1
mvn test
```

Requires Java 21+ and Maven.
