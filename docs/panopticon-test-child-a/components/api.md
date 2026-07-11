# api

## Responsibility

Exposes the REST API for querying and managing product inventory: listing inventory, reading and
updating a single SKU's stock level, and reserving/releasing stock for orders. Defines the
`inventory-api` interface via both its OpenAPI contract and its FastAPI route handlers. Also
defines a second, separate FastAPI app (`inventory/api/orders_routes.py`) implementing an
inventory-owned Orders API — this repo's own in-progress replacement for the orders service's
existing `orders-api`, still under `clients.orders` during migration (see
[clients](clients.md)). Request handling logic (persistence, ERP calls, event side effects) is
out of scope here — every handler in both apps returns placeholder data and neither calls any
other component in this repo.

## Interfaces

- **`inventory-api`** (`rest`) — owned/produced here. See
  [interfaces.md](../interfaces.md#inventory-api).
- **`orders-api`** (`rest`) — owned/produced here via `orders_routes.py`, alongside the orders
  service's own pre-existing `orders-api` declaration; this repo's own index self-claims
  ownership of the identical canonical name and type, an unreconciled ownership dispute (see
  [interfaces.md](../interfaces.md#orders-api)).

## Key modules

- `inventory/api/openapi.yaml` — the OpenAPI 3.0.3 contract: `GET /inventory`,
  `GET`/`PUT /inventory/{sku}`, `POST /inventory/reserve`, `POST /inventory/release`.
- `inventory/api/routes.py` — the FastAPI application (`app`) and route handlers implementing the
  contract above. Handlers currently return placeholder/stub responses (e.g. `list_inventory`
  always returns an empty list; `reserve_inventory` always returns `status: confirmed`).
- `inventory/api/orders_routes.py` — a separate FastAPI application (`app`) with `GET /orders`
  and `GET /orders/{order_id}`, both returning placeholder data. No OpenAPI contract file exists
  for it (unlike `inventory-api`).

## Configuration

None — `routes.py` reads no environment variables or files.

## Failure modes

Since handlers are stubs, there is no real failure mode yet beyond standard FastAPI/HTTP error
handling (e.g. `get_inventory_item` raises a 404 for any SKU, since it has no backing lookup).
Once handlers are implemented against `db`, `queue`, and `clients`, failures in those dependencies
would surface here.
