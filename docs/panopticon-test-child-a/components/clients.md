# clients

## Responsibility

Outbound HTTP clients for the Orders, warehouse, and order-processing-status endpoints. Each
client is a thin `httpx`-based wrapper with no retry, caching, or circuit-breaking logic. They
are not called from another component in this repository currently (see
[architecture.md](../architecture.md#data-flow)).

## Interfaces

- **`orders-api`** (`rest`) — consumed via `inventory/clients/orders.py`. See
  [interfaces.md](../interfaces.md#orders-api).
- **`warehouse-erp`** (`rest`) — consumed here. Its owner is not established by local source.
  See [interfaces.md](../interfaces.md#warehouse-erp).
- **`order-processing-status`** (`rest`) — consumed here via the status endpoint. Its owner is
  not established by local source. See
  [interfaces.md](../interfaces.md#order-processing-status).

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
- `WAREHOUSE_ERP_URL` — base URL for the warehouse endpoint. Required (read at import time in
  `erp.py`; missing value raises `KeyError` on import).
- `ORDER_PROCESSING_URL` — base URL for the order-processing status endpoint. Required (read at
  import time in `order_processing.py`; missing value raises `KeyError` on import).

## Failure modes

All three clients call `response.raise_for_status()`, so any non-2xx response from any upstream
raises an `httpx.HTTPStatusError`. None of them catch or retry — failures propagate directly to
the caller. All `_URL` environment variables are read at module import time, so a missing variable
fails at import rather than at call time.
