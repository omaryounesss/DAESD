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
| Remaining F1 organic/fallback routes | This run verified F2 and reused earlier F1 persistence evidence; coordinate certification-service demonstration with its owner |
| Review and merge order | Work is in draft PR #64 targeting the F2 feature branch. Main has not been merged; PR #60 and group integration order need coordinated review |
| Signed contribution matrix | Members must agree truthful contributions and sign for themselves |
| LESP and individual rehearsal | Explain concrete design implications, sources and trade-offs: access to catalogue/credentials, accurate product claims and traceability, accessible validation feedback, audit accuracy and AI acknowledgement |
| Final runtime rehearsal | Modeler layout and documentation were corrected on 24 November; the obsolete incoming correction message was removed. Runtime version 2 was live-tested before these presentation changes. Complete a fresh connected F1 certification run and combined F1/F2 rehearsal when the environment is Healthy |

Do not add more forms merely to increase their count. Protect time for a coherent, repeatable demonstration: F1 publishes -> producer updates/corrects -> catalogue changes -> availability decision -> notification receipt; then show review, seasonal and duplicate/timeout evidence.

This is a classroom system, with a single shared SQLite worker and a local simulated notification channel. Producer product-ownership enforcement, real payment-provider orchestration, email/SMS and production high availability are not claimed. Overselling is currently rejected as an incident without negative stock; upstream compensation/reservation remains an integration design issue.

## Final package checks - 24 November

- 45 Python tests pass after the layout/message cleanup.
- Camunda parser/schema validation passes for all four F1/F2 executable BPMNs (one Java validation test).
- 13 certification-registry tests pass locally. The existing certification-service implementation and F1 route-test sources have been incorporated from F1 commit `84a767f7b71373e15cd08773115fc535d8676bff`; test resource paths follow the integrated F1 folders and publication is explicitly doubled for routing tests.
- Embedded route execution remains subject to this session's loopback restriction; historical success is not presented as a current rerun.
- [Demo and Q&A guide](task1-demo-guide.md) and the current traceability supplement are included.
- At the fresh certification check, Hub reported the UWE environment Paused. It was resumed and became Healthy. F1 version-11 instance `2251799869051645` passed validation for `GB-ORG-05`, but remained at Request certification verification without a result. A credential-reusing launcher was prepared; actual worker completion is still pending. See [fresh check](task1-final-live-check-2026-11-24.md).

