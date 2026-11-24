# Task 1 final readiness

Submission deadline in the supplied brief: before 14:00 UK time on 10 December 2026. Keep all assessed artefacts and contribution evidence in the group repository. No report or recorded presentation is required; prepare a live demonstration and individual Q&A.

## Technical evidence now available

- Shared F1 publication/F2 catalogue persistence and actual stock-update/order history.
- Three linked F2 forms: submission, correction, administrator review, with business validation and protected output mappings.
- Native Tasklist invalid/corrected journey, three actual invalid submissions and administrator allowance, and a separate rejection branch.
- Per-product message-based seasonal scheduling through Camunda, including catch-up, ended-season and zero-stock behaviour.
- Separate simulated Notification Service, durable outbox and actual low-stock, zero-stock and correction receipts.
- Live duplicate-order protection using different message IDs for the same order ID.
- Isolated accelerated review-timeout path, leaving the assessed PT48H duration unchanged.
- Current runbook, executable mapping and detailed live test register, with honest distinctions between local checks, native execution and accelerated tests.

## Remaining submission gates

| Gate | Why it remains |
| --- | --- |
| Model-author review | Producer-task and seasonal-trigger refinements must align with the group-authored operational, strategic and i* models. This cannot be established by executable schema tests alone |
| Individual and group rehearsal | Fresh F1 version-11 verified/rejected organic routes and both manual outcomes were exercised with the actual certification worker. Repeat the agreed demonstration with members present; the 24-hour F1 escalation was not newly observed live |
| Review and merge order | Work is in draft PR #64 targeting the F2 feature branch. Main has not been merged; PR #60 and group integration order need coordinated review |
| Signed contribution matrix | Members must agree truthful contributions and sign for themselves |
| LESP and individual rehearsal | The complete [LESP review document](task1-lesp-considerations.md) is prepared with official references. Members must review the reasoning, resolve permitted-AI/authorship questions against the brief and rehearse their explanation |
| Final runtime presentation | Modeler layout and documentation were corrected on 24 November; the obsolete incoming correction message was removed. The connected F1-to-F2 journey was exercised after recovery. Deploy/rehearse the agreed final bundles together; presentation-only Modeler changes are not retroactive changes to existing instances |

Do not add more forms merely to increase their count. Protect time for a coherent, repeatable demonstration: F1 publishes -> producer updates/corrects -> catalogue changes -> availability decision -> notification receipt; then show review, seasonal and duplicate/timeout evidence.

This is a classroom system, with a single shared SQLite worker and a local simulated notification channel. Producer product-ownership enforcement, real payment-provider orchestration, email/SMS and production high availability are not claimed. Overselling is currently rejected as an incident without negative stock; upstream compensation/reservation remains an integration design issue.

## Final package checks - 24 November

- 45 Python tests pass after the layout/message cleanup.
- Camunda parser/schema validation passes for all four F1/F2 executable BPMNs (one Java validation test).
- 13 certification-registry tests pass locally. The existing certification-service implementation and F1 route-test sources have been incorporated from F1 commit `84a767f7b71373e15cd08773115fc535d8676bff`; test resource paths follow the integrated F1 folders and publication is explicitly doubled for routing tests.
- Embedded route execution remains subject to this session's loopback restriction; historical success is not presented as a current rerun.
- [Demo and Q&A guide](task1-demo-guide.md) and the current traceability supplement are included.
- The UWE environment was resumed from Paused to Healthy. Both workers were restarted with existing credentials. Five fresh F1 version-11 cases completed: verified organic, rejected/remove claim, rejected/withhold, three actual timeouts/manual approve, and three actual timeouts/manual reject. The verified product then passed through native F2 stock update and independent low-stock receipt acceptance. See [fresh check](task1-final-live-check-2026-11-24.md).

## Submission actions requiring people

The following proposals are prepared so members can review concrete work:

- [Model consistency review and C1-C8 decisions](task1-model-consistency-review.md)
- [Evidence-based contribution proposal](task1-contribution-proposal.md)
- [Merge order and final submission checklist](task1-merge-and-submission-plan.md)
- [Timed demonstration and proposed speaker roles](task1-timed-demonstration.md)
- [Assessment/route coverage and untested paths](task1-coverage-checklist.md)

Review version finalised on 24 November 2026: implementation, execution evidence, setup, traceability, demo/Q&A guide and LESP discussion are prepared for group feedback. This is the current review baseline; revise it through later commits if the group requests changes.

The technical review package is prepared in PR #64. It is not merged to main and is not a submitted assessment. The group must review model semantics and authorship, agree integration order with PR #60, agree/sign contributions individually, confirm the selected functionalities/demo arrangement with the module team and rehearse individual answers. No approval, signature or retrospective authorship certification is implied by this register.

