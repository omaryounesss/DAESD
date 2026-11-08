# Operational BPMN Models

**Module:** Distributed and Enterprise Software Development (UFCFTR-30-3)  
**Project:** Bristol Regional Food Network — Online Food Marketplace  
**Contributor:** Zain-Eldin Sharaf (Member 3)  
**Student ID:** 24061907

## Overview

This directory contains the operational BPMN models developed for Use Case 1: Producer Product Listing and Inventory Management.

The models expand the high-level activities identified in the group's strategic BPMN into detailed operational workflows, including user interactions, automated tasks, decision gateways, external service communication, exception handling and data management.

Two major functionalities are covered:

1. **Functionality 1:** Product Listing, Validation and Publication
2. **Functionality 2:** Inventory and Seasonal Availability Management

## Functionality 1 — Product Listing, Validation and Publication

### Purpose

This process allows registered producers to submit product listings to the marketplace. The platform validates the submitted information, verifies organic certification claims where applicable, and publishes approved listings to the product catalogue.

The process also handles invalid submissions, rejected certification claims, unavailable certification services and manual administrative reviews.

### BPMN Participants

| Participant | Responsibility |
|---|---|
| Producer | Submits product information, corrects invalid details and responds to rejected organic claims |
| Marketplace Platform | Validates product information, communicates with external services, manages publication and records traceability |
| Marketplace Administrator | Manually reviews certification evidence when automated verification cannot be completed |
| Organic Certification Service | Provides external verification of organic certification claims |

### Main Workflow

1. The producer submits product details to the marketplace.
2. The platform validates mandatory fields, pricing, stock quantities, seasonal dates, origin information, allergens and certification details.
3. Invalid submissions are returned to the producer for correction.
4. Valid submissions are checked for organic certification claims.
5. Where an organic claim exists, the platform requests verification from the external certification service.
6. Successfully verified products proceed to publication.
7. The platform prepares and saves the listing, records product traceability and publishes the product.
8. The producer receives a publication notification.

### Alternative and Exception Handling

| Scenario | Process Response |
|---|---|
| Invalid product details | Request corrections and repeat validation |
| No organic certification claim | Continue directly towards publication |
| Organic certification rejected | Notify producer and request a decision to remove the claim |
| Producer removes rejected claim | Remove the claim and continue publication |
| Producer retains rejected claim | Withhold the listing and notify the producer |
| Certification service timeout | Retry verification within the defined attempt limit |
| Repeated verification failure | Escalate to manual administrative review |
| Manual review approved | Record verified status and continue publication |
| Manual review rejected | Withhold the listing |
| Manual review exceeds 24 hours | Trigger a non-interrupting timer escalation and record the overdue review |

### BPMN Modelling Elements

The model includes:

- Message start and intermediate catch events
- User tasks, service tasks and send tasks
- Expanded subprocesses for product validation and manual certification review
- Exclusive and event-based gateways
- Message flows between the marketplace and external participants
- Timer events for certification timeouts and overdue manual reviews
- Alternative and exception paths
- Data objects and data stores for catalogue, certification and traceability information

### Product Traceability

A separate BPMN model, `record_product_traceability.bpmn`, documents the traceability-recording activity associated with product publication.

This supports the marketplace's requirement to maintain product origin and traceability information.

### Files

| File | Description |
|---|---|
| `functionality-1/product-listing.bpmn` | Editable operational BPMN model |
| `functionality-1/product-listing.png` | Image export |
| `functionality-1/product-listing.pdf` | PDF export |
| `functionality-1/record_product_traceability.bpmn` | Traceability BPMN model |
| `functionality-1/record_product_traceability.png` | Traceability image export |
| `functionality-1/record_product_traceability.pdf` | Traceability PDF export |

### Implementation Status

Functionality 1 is complete as a design-stage operational BPMN model. The executable Camunda implementation, including task workers, process variables and forms, is a separate group implementation activity.

## Functionality 2 — Inventory and Seasonal Availability Management

*Pending development.*

This section will be expanded once the second operational BPMN model has been completed.

