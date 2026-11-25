# Persistent seasonal scheduling through Camunda

Current design, 24 November 2026. This supersedes the earlier service-only scheduler and fixed single-product BPMN timer demonstration.

1. F1 publication or a changed F2 season creates start/end entries for the product's seasonVersion. A stock-only update keeps the schedule. Changing dates cancels pending and queued older entries in the same transaction.
2. The worker finds due pending entries and commits one stable-ID seasonal message intent to outbox, marking the schedule queued. It does not update availability here.
3. The dispatcher publishes f2-season-start or f2-season-end with product/version/boundary/due variables. Failed publication retains a retry time/error. Publication acknowledgement sets outbox sent=1; the schedule remains queued.
4. Camunda executes the original seasonal route. Each relevant worker job rejects stale version/date or premature boundaries, then uses current stock and the current date to calculate availability. Applying a matching boundary records season_events and marks season_schedule completed transactionally with the cached job result.

| State | Meaning |
| --- | --- |
| pending | Boundary has not been queued yet |
| queued | Durable publication intent or acknowledged publication awaiting business execution |
| completed | A matching seasonal job applied its current-state check |
| cancelled | A newer schedule superseded this boundary |

The end date is inclusive: the end action is due the following day. Boundaries are UTC. Restart catches missed dates. If both start and end were missed, current-date checks keep an ended season unavailable. Already published stale messages may still create harmless process instances; their jobs cannot apply the obsolete boundary. Exactly-once network delivery is not claimed.

The executable BPMN has message-based seasonal starts and no fixed timeDate values. The PT48H administrator boundary timer is separate and retained. The old F2_TIMER_PRODUCT_ID fallback exists only for old deployed timer instances; it is not used by new scheduler messages, and startup no longer seeds a product.

Historical schedule entries that were completed by the old service-only scheduler remain as historical records. They do not prove Camunda execution. Version-2 P1 seasonVersion 7 start/end were applied through live Camunda on 24 November; see the live report.

Queue/retry tests use temporary databases and injected transports; native live execution evidence is recorded separately. Operational source timer icons remain unchanged pending group-author review of the documented execution refinement.

