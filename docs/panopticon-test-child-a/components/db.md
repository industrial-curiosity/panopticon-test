# db

## Responsibility

Read access to the product catalog database: fetching a single product by SKU, listing products,
and searching products by name or SKU. Does not write to the database (no insert/update/delete
statements). Not called from any other component in this repo currently.

## Interfaces

- **`product-catalog-db`** (`database`) — consumed here; owned externally (managed RDS instance,
  no org repo owner). See [interfaces.md](../interfaces.md#product-catalog-db).

## Key modules

- `inventory/db/catalog.py` — `get_connection()` opens a `psycopg2` connection with
  `RealDictCursor`; `get_product(sku)`, `list_products(limit=100, offset=0)`,
  `search_products(query)` run read-only queries against a `products` table.

## Configuration

- `CATALOG_DB_DSN` — PostgreSQL DSN for the product catalog RDS instance. Required (read at
  import time; missing value raises `KeyError` on import).

## Failure modes

No error handling around the `psycopg2` calls — connection failures or query errors (bad DSN,
network, permissions) propagate directly to the caller. Each function opens and closes its own
connection (no pooling).
