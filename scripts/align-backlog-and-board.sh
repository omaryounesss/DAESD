#!/usr/bin/env bash
# Aligns GitHub Issues with the backlog IDs in docs/selected-functionalities.md §6
# and builds the Kanban board (GitHub Projects).
# Before running:  gh auth refresh -s project      (adds the "project" permission)
# Run ONCE from inside the DAESD folder:  bash scripts/align-backlog-and-board.sh
set -e
REPO="omaryounesss/DAESD"
ME=$(gh api user --jq .login)

echo "== Labels"
lbl(){ gh label create "$1" --color "$2" --description "$3" --repo "$REPO" --force >/dev/null; }
lbl "Must"   "b60205" "MoSCoW: Must have"
lbl "Should" "fbca04" "MoSCoW: Should have"
lbl "Could"  "0e8a16" "MoSCoW: Could have"
for p in 1 2 3 5 8; do lbl "pts: $p" "c2e0c6" "Story points"; done
lbl "E1 Product listing"      "1d76db" "Epic E1 (F1)"
lbl "E2 Inventory"            "5319e7" "Epic E2 (F2)"
lbl "E3 Modelling"            "0052cc" "Epic E3"
lbl "E4 Services and testing" "006b75" "Epic E4"
lbl "PM"                      "f9d0c4" "Project management"

echo "== Retire first-draft issues (superseded by the agreed backlog)"
for n in 1 2 3 4 5 $(seq 9 28); do
  gh issue close "$n" --repo "$REPO" --reason "not planned" \
    --comment "Superseded: backlog re-planned with the IDs from docs/selected-functionalities.md §6." >/dev/null 2>&1 || true
done

echo "== Rename completed Sprint 1 PM issues"
gh issue edit 7 --repo "$REPO" --title "PM-01 Repository setup: README, folders, .gitignore" --add-label "PM,Must" >/dev/null
gh issue edit 6 --repo "$REPO" --title "PM-02 Initial product backlog, milestones and Kanban board" --add-label "PM,Must" >/dev/null
gh issue edit 8 --repo "$REPO" --title "PM-03 Meeting notes 01–03" --add-label "PM,Should" >/dev/null

echo "== Create backlog issues"
NEW=()   # "url|owner|status"
# mk <ID> <title> <criteria> <MoSCoW> <pts> <epic label> <owner text> <sprint> <lead owner> <status>
mk(){
  body="**Acceptance criteria:** $3

**Owner:** $7
**Source:** docs/selected-functionalities.md §6"
  url=$(gh issue create --repo "$REPO" --title "$1 $2" --body "$body" \
        --label "$4,pts: $5,$6" --milestone "Sprint $8")
  echo "  $url  $1"
  NEW+=("$url|$9|${10}")
}
# Epic E1
mk E1-01 "Submit a new product with its details" "Form captures every product field; mandatory fields marked" Must 3 "E1 Product listing" "M4" 2 "M4 Omar Abdelaaty" Todo
mk E1-02 "Validate submissions" "Missing fields, price ≤ 0, negative quantity and invalid dates rejected with a reason" Must 3 "E1 Product listing" "M4" 2 "M4 Omar Abdelaaty" Todo
mk E1-03 "Show errors and allow correction" "Errors shown on the form; resubmission re-validated" Must 2 "E1 Product listing" "M4" 2 "M4 Omar Abdelaaty" Todo
mk E1-04 "Verify organic claims" "Claim checked with the certification service; unverified claim cannot be published as organic" Must 5 "E1 Product listing" "M4, M5" 2 "M4 Omar Abdelaaty" Todo
mk E1-05 "Handle certification service unavailable" "Timed retry; after the limit, task assigned to administrator" Must 5 "E1 Product listing" "M4, M5" 3 "M4 Omar Abdelaaty" Todo
mk E1-06 "Publish valid products automatically" "Product status = Published; visible in catalogue" Must 2 "E1 Product listing" "M4" 2 "M4 Omar Abdelaaty" Todo
mk E1-07 "Store traceability data with the product" "Origin, allergen and date fields saved and linked to producer" Should 2 "E1 Product listing" "M4" 3 "M4 Omar Abdelaaty" Todo
mk E1-08 "Tell the producer the submission outcome" "Confirmation shown or sent on publish or rejection" Could 2 "E1 Product listing" "M4" 3 "M4 Omar Abdelaaty" Todo
# Epic E2
mk E2-01 "Update quantity and season dates" "Update form for a published product" Must 3 "E2 Inventory" "M4" 2 "M4 Omar Abdelaaty" Todo
mk E2-02 "Reject invalid updates" "Negative quantity or end-before-start rejected with a reason" Must 2 "E2 Inventory" "M4" 2 "M4 Omar Abdelaaty" Todo
mk E2-03 "Make zero-stock products unavailable" "Quantity 0 → status Unavailable" Must 3 "E2 Inventory" "M4" 2 "M4 Omar Abdelaaty" Todo
mk E2-04 "Restocked products return only in season" "Quantity > 0 and within season → Available; otherwise stays Unavailable" Must 3 "E2 Inventory" "M4" 3 "M4 Omar Abdelaaty" Todo
mk E2-05 "Season start/end timers" "Timer events recalculate status on the dates" Should 5 "E2 Inventory" "M3, M4" 3 "M3 Zaineldin Sharaf" Todo
mk E2-06 "Sell-out alert to producer" "Notification sent; failure recorded" Should 3 "E2 Inventory" "M4, M5" 3 "M4 Omar Abdelaaty" Todo
mk E2-07 "Reduce-stock entry point for ordering" "Message start event accepts product and quantity; status recalculated" Should 3 "E2 Inventory" "M3, M4" 3 "M3 Zaineldin Sharaf" Todo
# Epic E3
mk E3-01 "Strategic BPMN of the whole marketplace" "Committed in models/strategic-bpmn/, with image export" Must 5 "E3 Modelling" "M1" 1 "M1 Omar Younes" Done
mk E3-02 "Case-study analysis and functional scope" "Committed in docs/; agreed with module team" Must 3 "E3 Modelling" "M1, M2, M3" 1 "M1 Omar Younes" "In Progress"
mk E3-03 "i* Strategic Dependency and Strategic Rationale models" "Actors, goals, softgoals, dependencies from §3.3 of the analysis" Must 8 "E3 Modelling" "M2" 2 "M2 Mohamed Alabweh" Todo
mk E3-04 "Operational BPMN for F1" "Lanes, user/service tasks, gateways, boundary events for F1-A1 to F1-E2" Must 8 "E3 Modelling" "M3" 2 "M3 Zaineldin Sharaf" Todo
mk E3-05 "Operational BPMN for F2" "Timer and message events, gateways for F2-A1 to F2-E2" Must 8 "E3 Modelling" "M3" 2 "M3 Zaineldin Sharaf" Todo
mk E3-06 "Traceability table: i* → strategic → operational → Camunda" "Same names at every level; table in docs/" Must 3 "E3 Modelling" "M1, M2, M3" 2 "M1 Omar Younes" Todo
# Epic E4
mk E4-01 "Simulated certification service" "Returns verified, rejected or unavailable on demand" Must 5 "E4 Services and testing" "M5, M4" 2 "M5 Mohamed Hamdy" Todo
mk E4-02 "Test every alternative and exception path" "Test log shows F1-A1 to F1-E2 and F2-A1 to F2-E2 run" Must 5 "E4 Services and testing" "M5" 3 "M5 Mohamed Hamdy" Todo
mk E4-03 "End-to-end demonstration of both processes" "Both run in Camunda from start to finish" Must 3 "E4 Services and testing" "M4" 3 "M4 Omar Abdelaaty" Todo
mk E4-04 "LESP evaluation" "Food information, organic claims, data protection, accessibility" Should 3 "E4 Services and testing" "M2 (M1 reviews)" 3 "M2 Mohamed Alabweh" Todo
mk E4-05 "README, repository evidence, signed contribution matrix" "Matrix reflects actual repository evidence" Must 2 "E4 Services and testing" "M5 (all)" 3 "M5 Mohamed Hamdy" Todo
# Sprint 1 PM items still open
mk PM-04 "Agree F1 and F2 with the module team" "Decision recorded on this issue and in selected-functionalities.md §9" Must 1 "PM" "All" 1 "M1 Omar Younes" "In Progress"
mk PM-05 "Sprint 1 review: presentation and ZIP submission" "ZIP submitted on Blackboard before Thu 29 Oct 14:00; presented in class" Must 2 "PM" "All (M5 submits)" 1 "M5 Mohamed Hamdy" "In Progress"

# Close completed items
for e in "${NEW[@]}"; do IFS='|' read -r u o s <<<"$e"
  if [ "$s" = Done ]; then gh issue close "$u" --comment "Done in Sprint 1." >/dev/null; fi
done

echo "== Assign issues to known GitHub accounts"
for e in "${NEW[@]}"; do IFS='|' read -r u o s <<<"$e"
  case "$o" in M5*) gh issue edit "$u" --add-assignee "$ME" >/dev/null || true;;
               M1*) gh issue edit "$u" --add-assignee omaryounesss >/dev/null 2>&1 || true;; esac
done
for n in 6 7 8; do gh issue edit $n --repo "$REPO" --add-assignee "$ME" >/dev/null || true; done

echo "== Kanban board"
P=$(gh project create --owner "$ME" --title "DAESD – Use Case 1 Board" --format json --jq .number)
gh project edit "$P" --owner "$ME" --visibility PUBLIC >/dev/null
gh project link "$P" --owner "$ME" --repo "$REPO" >/dev/null 2>&1 || echo "  (could not link project to repo – fine, the board still works)"
PID=$(gh project view "$P" --owner "$ME" --format json --jq .id)
gh project field-create "$P" --owner "$ME" --name "Owner" --data-type SINGLE_SELECT \
  --single-select-options "M1 Omar Younes,M2 Mohamed Alabweh,M3 Zaineldin Sharaf,M4 Omar Abdelaaty,M5 Mohamed Hamdy" >/dev/null
FIELDS=$(gh project field-list "$P" --owner "$ME" --format json)
# python helper (macOS has python3) instead of jq
fid(){ echo "$FIELDS" | python3 -c "import json,sys;d=json.load(sys.stdin);print(next(f['id'] for f in d['fields'] if f['name']=='$1'))"; }
oid(){ echo "$FIELDS" | python3 -c "import json,sys;d=json.load(sys.stdin);f=next(f for f in d['fields'] if f['name']=='$1');print(next(o['id'] for o in f['options'] if o['name']=='$2'))"; }
SF=$(fid Status); OF=$(fid Owner)

add(){ # add <issue url> <owner> <status>
  item=$(gh project item-add "$P" --owner "$ME" --url "$1" --format json --jq .id)
  gh project item-edit --id "$item" --project-id "$PID" --field-id "$SF" --single-select-option-id "$(oid Status "$3")" >/dev/null
  gh project item-edit --id "$item" --project-id "$PID" --field-id "$OF" --single-select-option-id "$(oid Owner "$2")" >/dev/null
  echo "  added $1 ($3)"
}
add "https://github.com/$REPO/issues/7" "M5 Mohamed Hamdy" Done
add "https://github.com/$REPO/issues/6" "M5 Mohamed Hamdy" Done
add "https://github.com/$REPO/issues/8" "M5 Mohamed Hamdy" Done
for e in "${NEW[@]}"; do IFS='|' read -r u o s <<<"$e"; add "$u" "$o" "$s"; done

echo
echo "Board: https://github.com/users/$ME/projects/$P"
echo "Done."
