

# Operational BPMN Models

| Field | Details |
|---|---|
| Module | Distributed and Enterprise Software Development (UFCFTR-30-3) |
| Project | Bristol Regional Food Network — Online Food Marketplace |
| Use Case | UC1 — Producer Product Listing and Inventory Management |
| Contributor | Zain-Eldin Sharaf (Member 3) |
| Functionalities | F1 — Product Listing, Validation and Publication; F2 — Inventory and Seasonal Availability Management |

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

### Purpose

This process allows registered producers to update product stock quantities and seasonal availability dates. The marketplace validates these updates and automatically determines whether products should remain available for purchase.

The process also handles invalid stock updates, low-stock and out-of-stock notifications, automatic seasonal availability changes, and stock reductions received from the ordering process.

### BPMN Participants

| Participant | Responsibility |
|---|---|
| Producer | Submits stock and seasonal availability updates and corrects invalid information |
| Marketplace Platform | Validates updates, manages stock quantities, determines availability and updates the product catalogue |
| Marketplace Administrator | Reviews invalid updates that exceed the permitted correction attempts |
| Notification Service | Receives low-stock and out-of-stock notification requests |
| Payment Provider | Represents the external message triggering stock reduction following a successful order |

### Main Workflow

1. The producer submits an updated stock quantity or seasonal availability period.
2. The platform validates the stock quantity and seasonal dates using an expanded validation subprocess.
3. Invalid updates are returned to the producer for correction.
4. Valid updates are saved to the Product Catalogue.
5. The platform checks whether the stock quantity is zero.
6. Products with zero stock are made unavailable and an out-of-stock notification is requested.
7. Products with remaining stock are checked against their seasonal availability dates.
8. Products within their season are made available, while products outside their season remain unavailable.
9. The platform checks whether the remaining stock is below the low-stock threshold and requests a notification where necessary.
10. The process ends once the stock status has been updated.

### Alternative and Exception Handling

| Scenario | Process Response |
|---|---|
| Invalid stock quantity or seasonal dates | Request corrections and repeat validation |
| Correction attempt limit exceeded | Escalate to Marketplace Administrator |
| Administrator allows another correction | Return the update for correction |
| Administrator rejects the update | End the process without applying the invalid update |
| Administrative review exceeds 48 hours | Trigger an interrupting timer and end the review as timed out |
| Stock quantity reaches zero | Make the product unavailable and request an out-of-stock notification |
| Product is outside its season | Keep the product unavailable |
| Product is restocked within its season | Make the product available |
| Product is restocked outside its season | Keep the product unavailable |
| Stock falls below the low-stock threshold | Request a low-stock notification |

### Automatic Seasonal Availability

The model includes two timer-triggered workflows:

- **Season start:** The platform checks the product's current stock quantity using the reusable `check_product_stock_status` process. Products with available stock can be made available when their season begins.
- **Season end:** The platform automatically makes products unavailable when their seasonal availability period ends.

These workflows maintain product availability without requiring a producer to submit another update when a season begins or ends.

### Stock Reduction Integration

A separate message-triggered workflow handles stock reductions following successful orders.

The platform reduces the stock quantity by the purchased amount, checks whether the product should remain available, requests low-stock or out-of-stock notifications where appropriate, and saves the final stock and availability status to the Product Catalogue.

This represents the inventory-management response to an order, rather than the ordering or payment process itself, which is outside the scope of this model.

### BPMN Modelling Elements

The model includes:

- Message start and intermediate catch events
- Timer start events for seasonal changes
- User tasks, service tasks and send tasks
- An expanded subprocess for stock and seasonal date validation
- A reusable call activity for checking product stock status
- Exclusive gateways for validation, stock levels and seasonal availability
- Message flows between the marketplace and external participants
- An interrupting boundary timer for overdue administrative reviews
- Correction loops, alternative paths and exception handling
- Data associations with the Product Catalogue

### Reusable Stock Status Process

A separate BPMN model, `check-product-stock-status.bpmn`, represents the reusable stock-checking activity.

The process retrieves the current stock quantity from the Product Catalogue and returns it for use by the calling workflow.

This process is referenced by the season-start automation through a call activity.

### Files

| File | Description |
|---|---|
| `functionality-2/inventory-seasonal-availability.bpmn` | Editable operational BPMN model |
| `functionality-2/inventory-seasonal-availability.png` | Image export |
| `functionality-2/inventory-seasonal-availability.pdf` | PDF export |
| `functionality-2/check-product-stock-status.bpmn` | Reusable stock-check BPMN model |
| `functionality-2/check-product-stock-status.png` | Stock-check image export |
| `functionality-2/check-product-stock-status.pdf` | Stock-check PDF export |

### Implementation Status

Functionality 2 is complete as a design-stage operational BPMN model, including the reusable stock-checking process and inventory integration point.

Executable Camunda implementation, including service task workers, process variables, timer configuration and external service integration, remains a separate group implementation activity.
