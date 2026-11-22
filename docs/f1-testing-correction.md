# F1 testing mistake and correction

Recorded by Omar Fathy, 22 November 2026. This is a retrospective record; no F1 process, form, worker, test or existing evidence file was changed for this entry.

## What went wrong

Omar identified that the earlier F1 execution/testing used a separately simplified executable diagram, rather than making Zain's original operational BPMN executable. Those initial tests therefore did not demonstrate implementation of the complete agreed operational model. A test passing on that reduced diagram was insufficient evidence for the required F1 scope; an earlier failed test should not automatically be interpreted as a defect in the operational model.

## How it was corrected

The simplified implementation was replaced with an executable refinement of Zain's original operational F1 model. The current `feature/camunda-f1-product-listing` branch states that its two executable processes preserve the operational model's pools, lanes, layout and names. It includes the expanded validation subprocess, correction loop, certification request/result handling, retry/timeout paths, manual administrative review, rejected-claim decision, publication/withholding outcomes, producer notifications and the reusable traceability process.

The active Camunda project is `f1-product-listing`. Its current contents were reviewed on 22 November: `product-listing-publication`, `record-product-traceability` and six forms. These were left unchanged.

## Corroborating history in Camunda

The Recently deleted page was inspected without restoring or deleting anything:

| Item | Type | Deleted on (as displayed by Camunda) | Visible contents |
|---|---|---|---|
| executable-camunda | Project | 8 November 2026, 16:56 | product-listing-executable; Submit product listing; Product correction; Rejected organic claim decision; Manual certification review; README |
| executable-camunda | Folder | 8 November 2026, 11:30 | No contents exposed in the list |
| Test | Project | 15 November 2026, 15:28 | product-listing-publication; record-product-traceability |

All three entries show Omar Abdelatty as the person who deleted them. The deleted-item list establishes names and deletion history, not the contents or execution behaviour of the old diagram. The explanation of the original mistake comes from Omar's account. The `Test` project contains the later process names; its deletion alone does not establish that those files were wrong.

## Evidence after correction

The existing evidence index on `feature/camunda-f1-product-listing` documents university-cluster execution on 15 November 2026 for `product-listing-publication`, version 3:

| Route | Recorded outcome |
|---|---|
| Valid non-organic listing | Published |
| Invalid details, corrected and revalidated | Published; validation executed twice |
| Verified organic claim | Published as verified organic |
| Rejected organic claim, producer removes claim | Published as non-organic |
| Rejected organic claim, producer keeps claim | Listing withheld |
| Service unavailable, three timeouts, manual review approved | Published after manual verification |

Sources: [F1 evidence index](https://github.com/omaryounesss/DAESD/blob/84a767f7b71373e15cd08773115fc535d8676bff/tests/evidence/camunda-f1/README.md), [F1 executable README](https://github.com/omaryounesss/DAESD/blob/84a767f7b71373e15cd08773115fc535d8676bff/camunda/README.md), and the accompanying 11-route Java test class. These are existing recorded results, not a claim that F1 was rerun on 22 November.

## Lesson applied to F2

Start from Zain's actual operational BPMN XML, retain its tasks, gateways, exception paths and reusable process, and add the technical execution properties. Check traceability before presenting runtime evidence. Keep local business-rule checks, engine tests and real Tasklist/Operate evidence distinct.
