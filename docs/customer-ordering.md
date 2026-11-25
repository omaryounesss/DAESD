## Corrected full horizontal version

Use `place-order-horizontal` in the ordering project. This is a complete duplicate of the existing executable operational inventory diagram, retaining every original task, gateway, pool, lane and stock/season path. The ordering entry and payment steps run left to right into its original purchase path. The vertical model is labelled `superseded-vertical-ordering` and has a separate process ID.

Only the ordering entry is a none start in this copy. Other incoming message names are isolated with `ordering-copy-` so they do not consume the original inventory process scheduler/producer messages. The original inventory diagram is unchanged. The deployment script includes all six F2 forms and the stock-status child process. Ordering form references use latest binding. Deploy the complete bundle from one candidate checkout.

An earlier definition was deployed as **Place an order - full operational F2 (simulated payment)**. Its first live rehearsal did not complete. The current repository candidate still requires complete native execution evidence; see [25 November verification](task1-verification-2026-11-25.md).

# Operational ordering demonstration

Deployed Camunda project: f2-ordering-operational. Process ID: f2_customer_ordering. The original stock-update and seasonal scheduling diagrams were not changed.

The ordering copy preserves the operational F2 purchase tasks: stock reduction, zero-stock and season checks, availability updates, low/out-of-stock producer notifications and final persistence.

Flow: load products; order form; validate stock and season; choose simulated payment outcome; authorize through the separate payment service; atomically recheck and reduce stock; capture on success or void authorization if stock became unavailable; follow the original F2 availability and notification branches; show the result form. Declined payments do not change stock. No money or card details are used. Customer emails are not sent.

The payment simulation listens on 127.0.0.1:8766 and records durable authorization/capture/void outcomes. The notification simulation listens on 127.0.0.1:8765. The updated inventory launcher starts both services when needed.

## Run

Stop the existing inventory worker first. Run only one worker per catalogue. From the DaESD directory:

```powershell
python f2-work/services/inventory-service/connect_f2.py --credentials "$HOME/Downloads/daesd-omar-f2-worker-springboot.properties"
```

In Tasklist start **Place an order - full operational F2 (simulated payment)**. Complete the order form, choose approve or decline in the payment user task, then inspect the result. Follow the service tasks in Operate.

## Validation and status

55 local tests pass, including payment retries, conflicting references, declined payment, insufficient stock, authorization cancellation after a stock race, and notification creation. Camunda confirmed **Project deployed!**. The updated worker was not restarted by this session; live execution remains unverified.

The earlier simple diagram remains in f2-tasklist-executable for history. Do not redeploy it: it shares the ordering process ID and would become the latest version again. Use the new ordering project for changes and deployment.

Rebuild: `python f2-work/scripts/build_ordering.py`.
Deploy the canonical horizontal diagram, stock child process and all six F2 forms together: `python f2-work/scripts/deploy_ordering.py`.

## Repeatable native check

After deploying and starting the current shared worker, run `python scripts/verify_ordering_live.py --credentials "$HOME/Downloads/daesd-omar-f2-worker-springboot.properties"` from the repository root. It checks four native journeys and the synthetic payment/notification receipts. It has not been reported as passed by this update.
