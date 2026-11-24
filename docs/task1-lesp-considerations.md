# Legal, ethical, social and professional considerations

Task 1 review version, 24 November 2026. Scope: the Bristol Regional Food Network product-listing and inventory processes, their forms, shared catalogue worker and simulated certification/notification services. This document records the project's reasoning, implemented safeguards and remaining deployment requirements. It does not certify legal compliance or group approval.

## Legal considerations

### Personal information and security

Producer names, farm locations and review notes may identify people. The ICO's UK GDPR guidance identifies minimisation, accuracy, limited retention, security and accountability among the principles governing personal-data processing [1]. For this project, the practical response is to use synthetic demonstration records, collect only information needed for listings and traceability, and keep credentials outside source control. Existing launchers read the local credentials file and pass values through process memory; they do not write new credential files into the repository.

The shared catalogue and Tasklist demonstration do not enforce which producer owns which product. Before using real producer data, Task 2 must introduce authenticated identity and product-level authorisation, decide the lawful basis and privacy information for processing, define retention/deletion rules and restrict access to logs and backups. Database persistence is not proof of secure access or an adequate retention policy. Screenshots and published test evidence must exclude credentials and unnecessary personal information.

### Food information and organic claims

GOV.UK states that producers or preparers wishing to sell or label food as organic require certification by an organic control body [2]. Our F1 workflow therefore separates a producer's claim from a verification result and provides rejected-claim and manual-review routes. The classroom registry deliberately returns predetermined outcomes; neither a matching code nor a synthetic manual approval establishes real certification. A deployed marketplace would need an authoritative verification arrangement, evidence of certificate scope/validity and accountable review procedures.

The Food Standards Agency's distance-selling guidance requires allergen information before purchase and at delivery [3]. F1 captures allergen and traceability information, but required text fields only establish that a value was supplied. They do not establish its truth or complete the customer-facing ordering/delivery obligations. Task 2 must carry accurate information through product display, checkout and fulfilment, and handle changes without silently replacing historical order information.

## Ethical considerations

Customers may rely on organic, origin, allergen and availability statements when deciding what to buy. Incorrect claims can undermine trust and, for allergens, create serious potential harm. The implementation validates supplied fields, withholds unverified claims through the relevant branches and records traceability. Its limitation is that format validation cannot independently verify real-world facts. Human review must assess genuine evidence rather than treat a successful software route as a factual guarantee.

Producer convenience must be balanced with accuracy. Correction forms display validation errors and permit repair instead of immediately losing a listing. Repeated invalid stock updates reach administrator review, with an explicit rejection/allowance decision and a review timeout. Review notes support explanation, but the system should not invite unnecessary sensitive details. In production, users need a way to query or challenge a decision and correct inaccurate records.

The paid-order interface raises a separate fairness issue: an accepted payment must not be mistaken for guaranteed stock. The current worker rejects insufficient stock without making quantity negative, but leaves an incident. Before real transactions, the ordering/payment owner must agree reservation, rejection, refund or compensation behaviour and a clear customer explanation. This limitation must remain visible in demonstrations and handover.

## Social considerations

Small producers may have varying technical confidence, connectivity and record-keeping practices. Native forms, explicit field labels, visible errors and separate correction tasks reduce reliance on API knowledge. Inclusive season-end dates and total-stock wording help prevent misunderstandings. These are usability measures; a full accessibility evaluation has not been completed. Task 2 should evaluate keyboard operation, screen-reader labels, focus after errors, understandable dates and messages, and recovery after interruption with representative users.

Accurate stock and seasonal availability can reduce failed purchases and help local producers manage sales. This is an intended benefit, not a measured reduction in waste or an established sustainability outcome. Notifications can support timely updates, but repeated alerts may become burdensome. The outbox and stable identifiers reduce duplicate effects; a real notification channel should additionally consider preferences, suitable timing, clear delivery status and recovery when a producer cannot receive an alert.

Certification outages can disadvantage producers by delaying publication. Timed retries and explicit manual review provide a route forward without silently granting an organic claim. The administrator workload and time to resolution should be monitored if the system is deployed.

## Professional considerations

### Evidence and maintainability

The repository distinguishes business-rule tests, schema checks, embedded route tests and native live execution. Current evidence includes 45 passing Python tests, 13 certification-registry tests, validation of four BPMNs, five fresh connected F1 certification cases and a connected F1-to-F2 stock/notification journey. Embedded Java sources compile, but full embedded route execution was blocked by the session's loopback restrictions. F1's 24-hour escalation was not freshly observed live; F2's 48-hour review timeout was tested using a separate accelerated fixture. These distinctions prevent overstating coverage.

Transactions, cached job results, business order identifiers, versioned schedules and an outbox make side effects auditable and retries safer. They do not make the single-worker SQLite demonstration highly available. The documentation explains dependencies, launchers, service contracts, failure states and restart behaviour so another member can reproduce the demonstration and identify limitations.

### Authorship and responsibility

AI assistance was used for supporting implementation, forms, executable BPMN refinements/layout, tests and documentation. The original operational source files were retained. This record must not be replaced with an unsupported statement that all submitted diagrams or changes were independently human-authored. The supplied assessment restricts AI-generated models/diagrams: the group must check the permitted-use wording against the actual assistance, resolve any uncertainty with the module team and ensure submitted work meets it. Group approval alone does not alter that requirement.

Each member must understand and explain their contribution, review changes attributed to them, and sign only their own agreed contribution record. Model authors must review the relationship between i*, strategic BPMN, operational BPMN and executable refinements. Review commits and PR #64 preserve proposed changes without treating them as merged or submitted work.

## Task 2 handover priorities

| Priority | Requirement before wider deployment |
| --- | --- |
| Access | Authenticate users, enforce producer ownership and administrator permissions |
| Information | Define privacy/retention arrangements and preserve accurate claims and allergen information throughout the purchase/delivery journey |
| Certification | Replace the demonstration registry with an authoritative service and evidence-backed review |
| Orders | Agree stock reservation and payment rejection/compensation contracts |
| Interaction | Evaluate accessibility/usability and provide understandable recovery/decision explanations |
| Operations | Define backups, recovery, monitoring and real notification delivery/preferences |

## Demonstration explanation

Our safeguards support accurate claims and stock, recoverable user errors and traceable service actions. We demonstrate these with synthetic data and separate simulations. Our current limits include shared product access, unverified real-world input, incident-based oversell handling and local notification receipts. Task 2 must address those limits before real users, payments or certification decisions are involved.

## References

Sources checked 24 November 2026. The ICO notes that its guidance is under review following the Data (Use and Access) Act; recheck guidance before deployment.

1. Information Commissioner's Office, [A guide to the data protection principles](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/).
2. GOV.UK, [Food labelling and packaging: organic food](https://www.gov.uk/food-labelling-and-packaging/organic-food).
3. Food Standards Agency, [Food allergen labelling and information requirements: technical guidance](https://www.gov.uk/government/publications/food-allergen-labelling-and-information-requirements-technical-guidance/food-allergen-labelling-and-information-requirements-technical-guidance), distance-selling sections.

Project evidence: [fresh connected checks](task1-final-live-check-2026-11-24.md), [F2 live register](f2-tasklist-live-validation-2026-11-24.md), [traceability](traceability.md) and [readiness register](task1-final-readiness.md).

