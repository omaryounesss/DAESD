# Camunda 8 Processes and Forms

Executable processes for Use Case 1. Owner: Omar Fathy (M4).

```
camunda/
├── processes/
│   ├── product-listing-publication.bpmn   F1: product listing, validation and publication
│   └── record-product-traceability.bpmn   Called by F1 to store traceability data
└── forms/                                 Camunda Forms used by the user tasks
```

Both processes are Zain's operational models (`models/operational-bpmn/functionality-1/`) made executable, with the same pools, lanes, layout and names. Design notes, the list of changes, business rules, variables and the certification-service contract: [docs/camunda-variables.md](../docs/camunda-variables.md).

## Deploying to Camunda 8 SaaS (Web Modeler)

1. Upload all 8 files (6 forms, 2 processes) into one Web Modeler project.
2. Click **Deploy** on the project and choose the environment. Every file in the project is deployed together. If you deploy files one at a time instead, deploy the forms first, then `record-product-traceability.bpmn`, then `product-listing-publication.bpmn`: the user tasks link to forms by ID and the call activity links to the traceability process by ID.
3. Start `product-listing-publication` with **Run**.
4. In **Tasklist**, open each task and click **Assign to me** before filling it in. Forms stay read-only until the task is assigned.
5. Follow the instance in **Operate**.

The workspace must have a deployment environment assigned by an organisation admin. Otherwise Deploy shows "No deployment environments available".

## Running locally (Camunda 8 Run)

Useful for testing without the university environment. Camunda 8 Run includes its own Java.

1. Download the Windows zip from https://downloads.camunda.cloud/release/camunda/c8run/ (version 8.10.x) and unzip it.
2. In the unzipped folder: `./c8run.exe start`. Stop it with `./c8run.exe stop`.
3. Deploy through the REST API (login `demo` / `demo`):
   ```
   curl -u demo:demo -X POST http://localhost:8080/v2/deployments \
     -F resources=@camunda/forms/product-listing.form  (… one -F per form) \
     -F resources=@camunda/processes/record-product-traceability.bpmn \
     -F resources=@camunda/processes/product-listing-publication.bpmn
   ```
4. Start an instance: `curl -u demo:demo -X POST http://localhost:8080/v2/process-instances -H "Content-Type: application/json" -d '{"processDefinitionId":"product-listing-publication"}'`
5. Open http://localhost:8080/tasklist and http://localhost:8080/operate and log in with `demo` / `demo`.

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
