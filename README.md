# DaESD Group Project: Bristol Regional Food Network

**Module:** UFCFTR-30-3 Distributed and Enterprise Software Development (UWE Bristol, 2026–27)
**Assessment:** Task 1, Group Project and In-class Demonstration
**Use case:** Use Case 1, Producer Product Listing and Inventory Management

## Overview

A marketplace where local producers list products for customers in the Bristol region. Our work focuses on how producers list products and manage stock.

### Major functionalities (to be confirmed with the module team)

1. **Product listing, validation and publication:** the producer submits product details, the system validates them, any organic certification claim is checked with a (simulated) external service, and the product is published.
2. **Inventory and seasonal-availability management:** the producer updates quantity and season. A product becomes unavailable when stock hits zero and becomes available again when restocked within its season.

## Team

| Member | Name | Student ID | Responsibility |
|---|---|---|---|
| 1 | Omar Younes | 24061906 | Business analysis and strategic BPMN |
| 2 | Mohamed Abweh | 24061946 | Stakeholder analysis and i* models |
| 3 | Zain-Eldin Sharaf | 24061907 | Operational BPMN modelling |
| 4 | Omar Fathy | 23077327 | Camunda 8 process automation and forms |
| 5 | Mohamed Ahmed | 24062049 | Certification service, testing and project evidence |

Full role breakdown: [docs/roles.md](docs/roles.md)

## Repository structure

```
DAESD/
├── models/       Strategic BPMN, i* (SD/SR) and operational BPMN models
├── camunda/      Executable Camunda 8 BPMN files and Forms
├── services/     Simulated organic-certification service and other service-task code
├── tests/        Test cases and testing evidence
├── docs/         Sprint plan, roles, meeting notes, contribution matrix
└── scripts/      Helper scripts (e.g. backlog setup)
```

## Project management

- **Backlog:** [GitHub Issues](https://github.com/omaryounesss/DAESD/issues), labelled by priority, type and member
- **Sprints:** [GitHub Milestones](https://github.com/omaryounesss/DAESD/milestones) (Sprint 1, 2, 3)
- **Sprint plan:** [docs/sprint-plan.md](docs/sprint-plan.md)
- **Meetings:** [docs/meetings](docs/meetings/README.md), with a fixed weekly meeting every Sunday from 17:00 to 19:00

## Sprint timeline

| Sprint | Starts | Focus |
|---|---|---|
| Sprint 1 | 12 Oct 2026 | Strategic process analysis and project setup |
| Sprint 2 | 2 Nov 2026 | i* models, operational BPMN, initial Camunda automation |
| Sprint 3 | 23 Nov 2026 | Final implementation, integration and demonstration |
| Submission | 10 Dec 2026, 14:00 | Final repository |

## Running the artefacts

Setup instructions for the Camunda 8 processes and the certification service will be added in Sprint 2.

## Contribution

Every member commits their own work from their own GitHub account. Final percentages are agreed using commit history, issues and meeting records. See [docs/contribution-matrix-template.docx](docs/contribution-matrix-template.docx).
