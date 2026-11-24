# F2 producer forms - executable refinement

Status: implemented locally on 24 November 2026; deployment and native Tasklist execution still require verification. The older live runs prove the message-based version only.

Uploaded both BPMNs and all three forms to the separate Camunda project [f2-tasklist-executable](https://hub.camunda.io/workspaces/92fa97e5-a7b4-4f61-8f95-8e16edc03f4c/projects/31fc8f52-d77b-47f0-8ffa-e7f9f93349bb). The submission form renders in Modeler with zero form problems. The refined diagram opens and its duplicate-process-ID error was resolved by moving the refinement out of the legacy F2 project. The legacy files were retained. The new project has not been deployed; Modeler still warns that the inherited season-start date is in the past, and the runtime has not yet been selected for this project. Deployment must not be mistaken for an isolated test: using the same process ID creates a new version on the shared cluster.

## User journey

Start a new instance of **F2 Inventory and Seasonal Availability** (`Process_0g8kz9d`) using the none start. The shared worker loads current catalogue products and generates an updateId. In Tasklist, open **Update stock and seasonal availability**, choose a product, enter its new total quantity and inclusive season dates, then complete the task. Validation and persistence remain automated.

If dates or quantity fail business validation, **Correct stock and seasonal availability** appears with the product, update ID, errors and submitted values. Completing this form reruns validation in the same instance. Three invalid attempts still lead to the existing administrator review, with allow/reject and the PT48H deadline.

There are three linked Camunda forms: `f2-stock-update`, `f2-stock-correction`, and `f2-inventory-review`. No producer Swagger message is needed for this journey. Form-level validation prevents blank fields and negative quantities; use reversed dates to demonstrate the business correction loop. The worker remains responsible for validating data from all entry points.

## Operational-to-executable changes

| Operational behaviour | Executable refinement |
| --- | --- |
| Producer submits stock/season data through a black-box participant | Additional none start  `f2-prepare-update` service task  native producer submission user task  existing validation merge |
| Corrected stock update received (`Event_0pab392`) | Same ID/outgoing/incoming flows, refined into native correction user task linked to the existing correction form |
| Administrator reviews repeated invalid submissions | Existing task and form retained |
| Order-paid message deducts stock | Message name, route and automated service tasks retained |
| Original model layout | Executable entry row added and lower layout shifted; original operational source files are unchanged |

This supersedes the earlier claim that the executable preserves every node type and the entire diagram exactly. Original sequence-flow endpoints are preserved; explicitly documented entry nodes/flows are added. Producer interaction is hosted in the executable marketplace, as with F1. The automated catalogue-loading task is placed in the producer-interaction row for readability. The group model author must review semantic consistency and provenance under the assessment rules; no claim is made that this executable replaces the group-authored operational artefact.

## Contracts and limits

- `f2-prepare-update` returns `productOptions` as `{label,value}` entries from SQLite, an automatically generated `UI-...` updateId, correctionAttempts=0 and an empty error list. Its response is cached by job key, so retries reuse the same ID.
- Submission outputs only productId, quantity, availableFrom and availableUntil. Correction outputs only quantity and dates; product identity and the correction counter are not editable form fields.
- Catalogue choices are a snapshot at task creation. The worker rechecks that the submitted product exists before saving. No dummy product is created when the catalogue is empty; publish through F1 and start a new update.
- This remains a shared-cluster classroom demo. Product ownership/producer authentication is not enforced by the dropdown or lane label; configure Tasklist authorisation separately before treating it as a production producer interface.
- `f2-stock-update` and `f2-order-paid` message starts still work. **New deployments use a correction user task, not `f2-stock-corrected`**. Existing waiting instances on the old version retain their message subscription and must be completed using the old contract.
- Fixed-date BPMN seasonal starts, service-side dynamic scheduler, recorded-only notifications and the incoming paid-order contract have not changed.
- No payment form is added to inventory. Payment-provider integration is outside this F2 producer refinement.

## Deploy and demonstrate

1. Stop the shared worker with Ctrl+C, then restart `services/inventory-service/start-f2.cmd` so it loads the new `prepare-update` handler. Confirm CONNECTED.
2. Deploy both files from `camunda/f2/processes` and **all three forms** together. The new producer forms bind to the deployment; do not deploy a BPMN without its forms. Use a new version; do not migrate old waiting instances merely to test this change.
3. Start a new instance using the none start. Select a product and submit reversed dates. Observe the correction task, correct the dates, complete it, and verify the same instance completes with the matching SQLite quantity.
4. In a separate instance, submit invalid dates three times and demonstrate administrator review. Show its form and decision route.
5. Confirm the existing paid-order message still reduces stock on a separately identified demonstration order.

Rebuild: `python scripts/build_f2.py`. Python checks: `python -m unittest discover -s tests -p 'test_*.py'`. Parser check: from `tests/camunda-f2`, `mvn -o -Dtest=ModelValidationTest test`. Embedded producer/correction engine tests are included in `InventoryProcessTest`; this session cannot execute their assertions because loopback sockets are denied. Native Tasklist form rendering and live completion must be recorded after deployment.

AI assisted the executable implementation, forms, code, tests and this mapping. The group must acknowledge that assistance accurately and explain the resulting logic; do not claim an AI-authored diagram as a group-authored operational model.

