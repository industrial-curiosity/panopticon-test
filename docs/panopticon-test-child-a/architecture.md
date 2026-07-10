# panopticon-test-child-a — architecture overview

## Purpose

`py-inventory-service` (package `inventory`) manages product inventory: querying and updating
stock levels, reserving and releasing stock for orders, and integrating with the systems that
feed and consume inventory state (warehouse ERP, order events, fulfillment tasks, and periodic
snapshots). It is a Python 3.11+ service built on FastAPI, with supporting modules for external
clients, event consumption, async task queueing, snapshot storage, and product catalog access.

## Components

- [api](components/api.md) — REST API for querying and managing inventory levels and stock
  reservations
- [clients](components/clients.md) — outbound HTTP clients for the orders service and the
  warehouse ERP
- [events](components/events.md) — Kafka consumer for order lifecycle events
- [queue](components/queue.md) — SQS producer/consumer for fulfillment tasks
- [storage](components/storage.md) — S3 client for daily inventory snapshots
- [db](components/db.md) — PostgreSQL access to the product catalog

## Data flow

As implemented today, these components are **not wired to one another** — each is a standalone
module with no cross-imports (verified: `api`, `events`, `queue`, `storage`, `clients`, and `db`
each only import third-party/stdlib packages, never each other). Concretely:

- `api` (`inventory/api/routes.py`) exposes the `inventory-api` REST interface
  (list/get/update inventory, reserve/release stock) but its handlers return placeholder data —
  they do not call `db`, `queue`, or `clients`.
- `events` (`inventory/events/kafka_consumer.py`) subscribes to the `order-events` Kafka topic
  and dispatches `order.created`/`order.cancelled` messages to handler stubs
  (`_on_order_created`, `_on_order_cancelled`) that are currently empty (`pass`).
- `queue` (`inventory/queue/fulfillment_queue.py`) provides enqueue/poll/delete operations
  against the `fulfillment-queue` SQS queue but is not called from `api` or `events`.
- `storage` (`inventory/storage/snapshots.py`) provides upload/download/list operations against
  the `inventory-snapshots` S3 bucket, called from nowhere else in this repo.
- `clients` (`inventory/clients/`) provides HTTP clients for `orders-api` and `warehouse-erp`,
  called from nowhere else in this repo.
- `db` (`inventory/db/catalog.py`) provides read access to `product-catalog-db`, called from
  nowhere else in this repo.

See [interfaces.md](interfaces.md) for the full interface list with ownership and direction.

## Dependencies

- **`orders-api`** (REST, external, owned by the order service) — order lookups; unavailability
  blocks anything that calls `inventory/clients/orders.py`.
- **`warehouse-erp`** (REST, external, third-party on-premise ERP) — warehouse stock levels and
  replenishment requests; unavailability blocks `inventory/clients/erp.py` callers.
- **`order-events`** (Kafka, external, owned by the order service) — order lifecycle events
  consumed by `events`; unavailability stalls order-driven inventory updates once the handlers
  are implemented.
- **`product-catalog-db`** (database, external, managed RDS instance) — product metadata;
  unavailability blocks `inventory/db/catalog.py` callers.

Full details, ownership, and consumers/producers for every interface: see
[interfaces.md](interfaces.md).
