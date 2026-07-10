# clients

## Responsibility

Outbound HTTP clients for two external REST services this repo does not own: the orders service
and the warehouse ERP. Each client is a thin `httpx`-based wrapper — no retry, caching, or
circuit-breaking logic. Not called from any other component in this repo currently (see
[architecture.md](../architecture.md#data-flow)).

## Interfaces

- **`orders-api`** (`rest`) — consumed here; owned by the order service, not this repo. See
  [interfaces.md](../interfaces.md#orders-api).
- **`warehouse-erp`** (`rest`) — consumed here; owned externally (third-party on-premise ERP,
  no org repo owner). See [interfaces.md](../interfaces.md#warehouse-erp).

## Key modules

- `inventory/clients/orders.py` — `get_order(order_id)` and `list_orders(status=None)` against
  the orders service.
- `inventory/clients/erp.py` — `get_warehouse_stock(sku)` and
  `request_replenishment(sku, quantity)` against the warehouse ERP.

## Configuration

- `ORDERS_API_URL` — base URL for the orders service REST API. Required (read at import time in
  `orders.py`; missing value raises `KeyError` on import).
- `WAREHOUSE_ERP_URL` — base URL for the on-premise warehouse ERP. Required (read at import time
  in `erp.py`; missing value raises `KeyError` on import).

## Failure modes

Both clients call `response.raise_for_status()`, so any non-2xx response from either upstream
raises an `httpx.HTTPStatusError`. Neither client catches or retries — failures propagate directly
to the caller. Both `_URL` environment variables are read at module import time, so a missing
variable fails at import rather than at call time.
