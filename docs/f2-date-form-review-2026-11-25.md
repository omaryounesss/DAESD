# F2 date-picker form review - 25 November 2026

Reviewed Omar's downloaded exports `f2-stock-correction.form` and `f2-stock-update.form` from 25 November. Both use schemaVersion 19, executionPlatformVersion 8.9.0 and date-only datetime controls. Original downloaded files were not edited.

## Finding and correction

Replacing the text fields created new generated variable keys. Those keys do not match the BPMN output mappings or the worker contract:

| Form | Exported key | Correct process key |
| --- | --- | --- |
| Correction, season start | datetime_noqkeb | availableFrom |
| Correction, season end | datetime_vxd2o | availableUntil |
| Update, season start | datetime_d9f7e | availableFrom |
| Update, season end | datetime_ol4k5j | availableUntil |

Without correction, the process can receive missing or previously stored season values rather than the newly selected dates. Date-picker controls themselves are compatible with the existing date-only ISO contract already used by F1. Display format is distinct from the submitted `YYYY-MM-DD` value; time and timezone fields are not requested.

Corrected copies retain the exported form IDs, date-only subtype, required validation, component IDs, schema/export metadata and layout. Only the four variable keys were changed. Product selection, quantity, errors and context fields are preserved. Source copies are under `source/forms`; `scripts/build_f2.py` validates their contract and copies them to `camunda/f2/forms` instead of regenerating the old text controls.

## Verification

The build completed and all 46 Python tests passed. Existing mapping tests check exact output keys. The new contract regression checks both corrected form definitions and their source copies, exercises the worker with ISO date-only values, verifies invalid date order still fails and confirms the valid dates persist. These are local contract checks, not a new browser rendering or native Tasklist execution test. The browser connection was unavailable, so the new schema-19 exports have not been newly rendered/submitted against the live Tasklist by this check.

## Complete the Camunda change

Either import the corrected files from `camunda/f2/forms` or change the four Key properties in the existing Modeler controls to the correct process keys above. Do not rename their form IDs. Wait for autosave. Deploy both F2 BPMNs and all three forms together because the user tasks use deployment binding. Start a new instance and exercise invalid dates -> correction -> valid dates; confirm the resulting variables and catalogue dates. Existing instances retain their earlier deployment bindings; redeployment does not automatically repair an already bound form.

GitHub preserves the corrected export and generator support, but does not automatically update Camunda. This check makes no changes to running instances, deployed versions or the live database.

