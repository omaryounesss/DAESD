# Meeting 07: Functionality 2 Worker Walkthrough

| | |
|---|---|
| **Date** | Monday 23 November 2026 |
| **Time** | 18:00 - 20:00 |
| **Location** | Omar & Zain's House |
| **Meeting lead** | Omar Abdelaaty (Member 4) |
| **Notes by** | Mohamed Hamdy (Member 5) |

## Attendance

| Member | Name | Present |
|---|---|---|
| 1 | Omar Younes | ✅ |
| 2 | Mohamed Alabweh | ✅ |
| 3 | Zaineldin Sharaf | ✅ |
| 4 | Omar Abdelaaty | ✅ |
| 5 | Mohamed Hamdy | ✅ |

## Agenda

1. Walk through the Functionality 2 (inventory and seasonal availability) worker.
2. Show the team how to run and deploy F2 on the UWE Frenchay 2026 cluster.
3. Agree the next steps for Sprint 3.

## Discussion

**What Omar Abdelaaty built**
- F2's executable process follows Zaineldin Sharaf's operational BPMN.
- A Python worker (`services/inventory-service/worker.py`) does the automated work: it validates quantity and season dates, saves updates, reduces stock for paid orders, and records low-stock and zero-stock notifications.
- Business data is kept in a local SQLite database. Each job's result is stored, so a repeated job does not change stock twice.
- Availability rule: a product is available only when quantity is above 0 **and** today is within its season.

**How to run and deploy**
- Start the worker with the launcher (`start-f2.cmd`), which loads the credentials, checks the connection to the cluster and then starts the worker.
- The worker must stay running during a demo. If it stops, service tasks wait until it comes back.
- Credentials are loaded from the downloaded file and must never go into source code, screenshots or GitHub.
- In Operate, select process `Process_0g8kz9d` and include Completed and Incidents to see the results.

**Testing so far (23 Nov)**
- 27 local Python checks passed.
- 9 live F2 instances completed on the uni cluster: valid updates, paid-order stock deductions, low and zero stock, out of season, invalid data with corrections, and administrator review.
- Not yet tested: the seasonal BPMN timers and the 48-hour review timeout.
- Notifications are recorded in the database, not yet sent by email.

**Branch status**
- F2 work is on its own branch and has not been merged into `main`.

## Decisions

| # | Decision |
|---|---|
| D1 | F2 stays on its branch until the group agrees to merge it into `main`. |
| D2 | The team uses Omar's walkthrough to run F2 for testing and the demo. |
| D3 | The seasonal scheduling approach is agreed with Zaineldin Sharaf before it is changed, so there is one seasonal mechanism in the final design. |

## Actions

| # | Action | Owner |
|---|---|---|
| A1 | Send the team a walkthrough video of running and deploying F2 | Omar Abdelaaty (done after the meeting) |
| A2 | Push the latest connection changes, startup steps and live-test report to the F2 branch | Omar Abdelaaty |
| A3 | Test the seasonal timers and the review timeout | Omar Abdelaaty |
| A4 | Agree the seasonal scheduling approach | Omar Abdelaaty, Zaineldin Sharaf |
| A5 | Add F2's exception paths to the Sprint 3 test plan (E4-02) | Mohamed Hamdy |
| A6 | Update the board for F2 items (E2-01 to E2-07) | Mohamed Hamdy |
