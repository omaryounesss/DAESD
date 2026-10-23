#!/usr/bin/env bash
# Creates labels, sprint milestones and backlog issues on GitHub.
# Needs: GitHub CLI (brew install gh) and `gh auth login`.
# Run once from inside the DAESD folder:  bash scripts/setup-backlog.sh
set -e
REPO="omaryounesss/DAESD"

echo "== Labels"
lbl(){ gh label create "$1" --color "$2" --description "$3" --repo "$REPO" --force; }
lbl "priority: high"   "d73a4a" "Must be done this sprint"
lbl "priority: medium" "fbca04" "Should be done this sprint"
lbl "priority: low"    "0e8a16" "Nice to have"
lbl "type: model"      "5319e7" "BPMN / i* models"
lbl "type: camunda"    "1d76db" "Camunda processes and Forms"
lbl "type: service"    "006b75" "Service-task / supporting code"
lbl "type: testing"    "c5def5" "Testing and test evidence"
lbl "type: docs"       "bfdadc" "Documentation and README"
lbl "type: pm"         "f9d0c4" "Project management"
lbl "M1 Omar Younes"       "ededed" "Member 1"
lbl "M2 Mohamed Abweh"     "ededed" "Member 2"
lbl "M3 Zain-Eldin Sharaf" "ededed" "Member 3"
lbl "M4 Omar Fathy"        "ededed" "Member 4"
lbl "M5 Mohamed Ahmed"     "ededed" "Member 5"

echo "== Milestones"
ms(){ gh api "repos/$REPO/milestones" -f title="$1" -f due_on="$2" -f description="$3" >/dev/null 2>&1 || echo "  (milestone '$1' exists)"; }
ms "Sprint 1" "2026-11-01T23:59:00Z" "Strategic analysis and project setup"
ms "Sprint 2" "2026-11-22T23:59:00Z" "i* models, operational BPMN, initial Camunda automation"
ms "Sprint 3" "2026-12-10T13:00:00Z" "Final implementation, integration and demonstration"

echo "== Issues"
# iss <milestone> <labels> <title> <body> [close]
iss(){
  url=$(gh issue create --repo "$REPO" --milestone "$1" --label "$2" --title "$3" --body "$4")
  echo "  $url"
  [ "$5" = "close" ] && gh issue close "$url" --comment "Done." >/dev/null
  return 0
}

# Sprint 1
iss "Sprint 1" "priority: high,type: model,M1 Omar Younes" "Strategic BPMN model of the whole marketplace" "High-level BPMN of the Bristol Regional Food Network: major processes, actors, external organisations and interactions."
iss "Sprint 1" "priority: high,type: docs,M1 Omar Younes" "Identify major business processes" "List and briefly analyse the main business processes and organisational responsibilities from the case study."
iss "Sprint 1" "priority: high,type: docs,M2 Mohamed Abweh" "Stakeholder and responsibility analysis" "Identify stakeholders, their goals and responsibilities. Feeds the i* models in Sprint 2."
iss "Sprint 1" "priority: high,type: docs,M1 Omar Younes,M3 Zain-Eldin Sharaf" "Scope the two candidate major functionalities" "Define (1) product listing, validation and publication and (2) inventory and seasonal availability: start/end, actors, main/alternative/exception paths."
iss "Sprint 1" "priority: high,type: pm,M1 Omar Younes,M2 Mohamed Abweh,M3 Zain-Eldin Sharaf,M4 Omar Fathy,M5 Mohamed Ahmed" "Agree the two functionalities with the module team" "Present the two functionalities to the tutor and record the outcome in meeting notes."
iss "Sprint 1" "priority: high,type: pm,M5 Mohamed Ahmed" "Initial product backlog and sprint plan" "Create labels, milestones and backlog issues; write docs/sprint-plan.md." close
iss "Sprint 1" "priority: high,type: docs,M5 Mohamed Ahmed" "Repository setup: README, folders, .gitignore" "Main README, folder layout (models, camunda, services, tests, docs), .gitignore, roles doc and contribution matrix template." close
iss "Sprint 1" "priority: medium,type: pm,M5 Mohamed Ahmed" "Meeting notes 01–02" "Document meetings 01 (use-case selection) and 02 (roles) in docs/meetings." close
iss "Sprint 1" "priority: low,type: model,M2 Mohamed Abweh" "Start i* modelling" "Early draft of actors and dependencies. Not assessed until Sprint 2."

# Sprint 2
iss "Sprint 2" "priority: high,type: model,M2 Mohamed Abweh" "i* Strategic Dependency (SD) model" "Actors, goals, softgoals, tasks, resources and dependencies."
iss "Sprint 2" "priority: high,type: model,M2 Mohamed Abweh" "i* Strategic Rationale (SR) model" "Internal rationale of key actors, including trade-offs and competing goals."
iss "Sprint 2" "priority: high,type: model,M3 Zain-Eldin Sharaf" "Operational BPMN: product listing, validation and publication" "Pools/lanes, user and service tasks, gateways, message flows, events, alternative and exception paths (invalid data, certification rejected, service unavailable)."
iss "Sprint 2" "priority: high,type: model,M3 Zain-Eldin Sharaf" "Operational BPMN: inventory and seasonal availability" "Stock updates, auto-unavailable at zero stock, re-availability within season, exception paths."
iss "Sprint 2" "priority: medium,type: docs,M1 Omar Younes,M2 Mohamed Abweh,M3 Zain-Eldin Sharaf" "Traceability between i*, strategic and operational BPMN" "Show how stakeholder goals map to strategic and operational processes."
iss "Sprint 2" "priority: high,type: camunda,M4 Omar Fathy" "Camunda 8 process: product listing" "Executable process with user tasks, variables, gateways and business rules."
iss "Sprint 2" "priority: high,type: camunda,M4 Omar Fathy" "Camunda 8 process: inventory and seasonal availability" "Executable process for stock and season updates."
iss "Sprint 2" "priority: high,type: camunda,M4 Omar Fathy" "Camunda Forms for producer user tasks" "Product submission, correction and stock-update forms."
iss "Sprint 2" "priority: high,type: service,M5 Mohamed Ahmed" "Simulated organic-certification service" "Small service returning verified / rejected / unavailable for a certification number."
iss "Sprint 2" "priority: high,type: service,M5 Mohamed Ahmed,M4 Omar Fathy" "Connect certification service to Camunda service task" "Call the service from the listing process and map the result to process variables."

# Sprint 3
iss "Sprint 3" "priority: high,type: camunda,M4 Omar Fathy" "End-to-end execution of both processes" "Both workflows run start to finish in Camunda."
iss "Sprint 3" "priority: high,type: camunda,M4 Omar Fathy" "Finalise Forms and form-to-process data flow" "Confirm form data flows correctly through validation, verification and publication."
iss "Sprint 3" "priority: high,type: service,M4 Omar Fathy,M5 Mohamed Ahmed" "Service integration and failure handling" "Reliable request/response, timeouts, retries and error boundary events."
iss "Sprint 3" "priority: high,type: testing,M5 Mohamed Ahmed,M3 Zain-Eldin Sharaf" "Test alternative and exception paths" "Test invalid data, rejected certification and service-unavailable paths; save evidence in tests/."
iss "Sprint 3" "priority: medium,type: docs,M2 Mohamed Abweh,M1 Omar Younes" "Legal, ethical, social and professional (LESP) evaluation" "Accurate product info, honest organic claims, data protection, accessibility, auditability."
iss "Sprint 3" "priority: medium,type: docs,M1 Omar Younes,M2 Mohamed Abweh,M3 Zain-Eldin Sharaf,M4 Omar Fathy,M5 Mohamed Ahmed" "Model consistency and Task 2 readiness" "Check i*, strategic BPMN, operational BPMN and Camunda tell the same story; organise for reuse in Task 2."
iss "Sprint 3" "priority: medium,type: docs,M5 Mohamed Ahmed" "Final README, testing evidence and repository tidy-up" "Setup/run instructions and final repo organisation."
iss "Sprint 3" "priority: high,type: pm,M1 Omar Younes,M2 Mohamed Abweh,M3 Zain-Eldin Sharaf,M4 Omar Fathy,M5 Mohamed Ahmed" "Signed contribution matrix" "Agree percentages from real evidence and upload the signed matrix."
iss "Sprint 3" "priority: high,type: pm,M1 Omar Younes,M2 Mohamed Abweh,M3 Zain-Eldin Sharaf,M4 Omar Fathy,M5 Mohamed Ahmed" "Demo preparation and Q&A rehearsal" "Each member presents their area and can explain the full workflow."

echo "Done."
