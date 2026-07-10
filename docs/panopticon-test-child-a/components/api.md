# api

## Responsibility

Exposes the REST API for querying and managing product inventory: listing inventory, reading and
updating a single SKU's stock level, and reserving/releasing stock for orders. Defines the
`inventory-api` interface via both its OpenAPI contract and its FastAPI route handlers. Request
handling logic (persistence, ERP calls, event side effects) is out of scope here — the current
handlers return placeholder data and do not call any other component in this repo.

## Interfaces

- **`inventory-api`** (`rest`) — owned/produced here. See
  [interfaces.md](../interfaces.md#inventory-api).

## Key modules

- `inventory/api/openapi.yaml` — the OpenAPI 3.0.3 contract: `GET /inventory`,
  `GET`/`PUT /inventory/{sku}`, `POST /inventory/reserve`, `POST /inventory/release`.
- `inventory/api/routes.py` — the FastAPI application (`app`) and route handlers implementing the
  contract above. Handlers currently return placeholder/stub responses (e.g. `list_inventory`
  always returns an empty list; `reserve_inventory` always returns `status: confirmed`).

## Configuration

None — `routes.py` reads no environment variables or files.

## Failure modes

Since handlers are stubs, there is no real failure mode yet beyond standard FastAPI/HTTP error
handling (e.g. `get_inventory_item` raises a 404 for any SKU, since it has no backing lookup).
Once handlers are implemented against `db`, `queue`, and `clients`, failures in those dependencies
would surface here.
