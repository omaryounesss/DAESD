# Proposed merge order and submission checklist

Prepared 24 November 2026. Read-only branch/PR inspection; no merge, retarget or main change was performed. Deadline from the supplied brief: before 14:00 UK time on 10 December 2026.

## Current branch facts

| Item | Observed position |
| --- | --- |
| main | 5f6395d101463def83dfaa545d1c963f3190186b; already contains i*, strategic and both operational source models and exports |
| F1 feature | feature/camunda-f1-product-listing at 84a767f7b71373e15cd08773115fc535d8676bff |
| PR #60 | Open: F1 feature -> docs/operational-bpmn-models; uses older camunda/processes and camunda/forms layout |
| F2 feature | feature/camunda-f2-inventory-seasonal at 7f1d066c2a28bc2a9732f104876536e65413d6d6 |
| PR #64 | Draft: review/task1-integration-evidence-20261124 -> F2 feature; contains connected camunda/f1 and camunda/f2 bundles and current services/evidence |

The review branch's 23 source-model blobs match main at inspection. This is a file-content comparison, not proof the branch is up to date in ancestry or conflict-free. The connector did not provide a branch-compare endpoint; a maintainer must inspect the final diff/conflicts in GitHub or a normal Git checkout.

## Recommended integration sequence

1. Freeze an agreed review commit and record its SHA. Complete the [model decisions](task1-model-consistency-review.md), permitted-AI review and contributor checks first. Do not wait for an operational-model merge that has already reached main.
2. Resolve PR #60 with its author/maintainer before combining executable branches. Compare its F1 files against the connected equivalents in camunda/f1, the certificate service and test sources already included by PR #64. Preserve original authorship/history. Decide explicitly whether to retain it as historical/superseded work or integrate any unique changes. Do not blindly merge both directory layouts or close another proposal without agreement.
3. After approval, merge PR #64 into the F2 feature branch as currently targeted. Resolve conflicts preserving connected F1 publication (`f1-publish-product`), current F2 native forms and message-based scheduler. Keep the original source-model files intact unless their authors approve an intentional change.
4. Open a separate final F2-feature -> main integration PR. Review the complete diff, ensure any desired F1/service history is represented, remove ambiguous duplicate deployment paths and choose one documented setup. Keep credentials, live databases, build outputs and Python caches out of the commit.
5. Run checks and the main rehearsal against that candidate. Deploy each functionality's process/form bundle consistently; record resulting versions. Use the candidate checkout and database path for the demo rather than an untracked local variant.
6. After actual maintainer approval, merge the final integration PR. Recheck main, record the submitted commit SHA and link, confirm the brief's submission mechanism and submit before the deadline. No merge or assessment submission is authorised by this document itself.

## Final repository checklist

- [ ] Agreed main commit recorded; both assessed functionalities identified and module-team agreement reference included if required.
- [ ] i* SD/SR, strategic model and two operational models included with current exports and traceability.
- [ ] Two F1 BPMNs/six forms and two F2 BPMNs/three forms included; form IDs and deployment binding correct.
- [ ] Certification service, shared worker, scheduler, notification receiver and setup instructions included.
- [ ] No competing or obsolete deployment bundle is presented as the current executable.
- [ ] Credentials, tokens, producer personal information and live database files excluded; screenshots reviewed.
- [ ] Checks and reproducible evidence linked; historical, native, mocked and accelerated results clearly distinguished.
- [ ] [Coverage](task1-coverage-checklist.md), [LESP](task1-lesp-considerations.md) and [consistency decisions](task1-model-consistency-review.md) reviewed.
- [ ] Contribution matrix agreed and individually signed; AI acknowledgement accurately covers actual assistance.
- [ ] Demo duration/arrangement confirmed; all members rehearse their own explanations.
- [ ] Final repository link and exact submission commit checked through the required submission route.

## Recovery if feedback requires changes

Make a follow-up commit/PR with the review decision and reason; keep existing evidence identifiable. Redeploy the relevant complete bundle and rerun affected scenarios when behaviour changes. Existing Camunda instances retain their deployed version. Use fresh synthetic IDs and preserve audit records. Avoid rewriting shared history or resetting demonstration stock indiscriminately.

