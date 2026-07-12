# clients

## Responsibility

Outbound HTTP clients for external REST services this repo does not own: the orders service, the
warehouse ERP, and an order-processing status endpoint. Each client is a thin `httpx`-based
wrapper — no retry, caching, or circuit-breaking logic. Not called from any other component in
this repo currently (see [architecture.md](../architecture.md#data-flow)).

## Interfaces

- **`orders-api`** (`rest`) — consumed here via `inventory/clients/orders.py` against the order
  service's existing API; this repo's own index also self-claims ownership of the identical
  canonical name and type via `api/orders_routes.py` (see [api](api.md)) — an unreconciled
  ownership dispute, not a resolved handoff. See [interfaces.md](../interfaces.md#orders-api).
- **`warehouse-erp`** (`rest`) — consumed here; owned externally (third-party on-premise ERP,
  no org repo owner). See [interfaces.md](../interfaces.md#warehouse-erp).
- **`order-processing-queue`** (`rest`) — consumed here; owned externally, name unresolved (no
  owner recorded in this repo's index; this repo has no visibility into other repos' declarations).
  See [interfaces.md](../interfaces.md#order-processing-queue).

## Key modules

- `inventory/clients/orders.py` — `get_order(order_id)` and `list_orders(status=None)` against
  the orders service.
- `inventory/clients/erp.py` — `get_warehouse_stock(sku)` and
  `request_replenishment(sku, quantity)` against the warehouse ERP.
- `inventory/clients/order_processing.py` — `get_processing_status(order_id)` against an
  order-processing status endpoint.

## Configuration

- `ORDERS_API_URL` — base URL for the orders service REST API. Required (read at import time in
  `orders.py`; missing value raises `KeyError` on import).
- `WAREHOUSE_ERP_URL` — base URL for the on-premise warehouse ERP. Required (read at import time
  in `erp.py`; missing value raises `KeyError` on import).
- `ORDER_PROCESSING_URL` — base URL for the order-processing status endpoint. Required (read at
  import time in `order_processing.py`; missing value raises `KeyError` on import).

## Failure modes

All three clients call `response.raise_for_status()`, so any non-2xx response from any upstream
raises an `httpx.HTTPStatusError`. None of them catch or retry — failures propagate directly to
the caller. All `_URL` environment variables are read at module import time, so a missing variable
fails at import rather than at call time.
