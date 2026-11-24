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
| Final Modeler draft | Replace the previous review draft with the current executable so it matches live version 2; do not redeploy the old fixed-date draft |

Do not add more forms merely to increase their count. Protect time for a coherent, repeatable demonstration: F1 publishes -> producer updates/corrects -> catalogue changes -> availability decision -> notification receipt; then show review, seasonal and duplicate/timeout evidence.

This is a classroom system, with a single shared SQLite worker and a local simulated notification channel. Producer product-ownership enforcement, real payment-provider orchestration, email/SMS and production high availability are not claimed. Overselling is currently rejected as an incident without negative stock; upstream compensation/reservation remains an integration design issue.

