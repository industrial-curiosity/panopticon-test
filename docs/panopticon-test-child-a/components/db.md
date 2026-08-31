---
type: component
---

# db

## Responsibility

The `db` component provides catalog queries against the product catalog database. It opens a
PostgreSQL connection with `RealDictCursor` and exposes helpers to fetch one product, list products,
or search products by name or SKU.

## Interfaces

The component consumes `product-catalog-db`. See [interfaces.md](../interfaces.md) for the indexed
entry.

## Key modules

- `inventory/db/catalog.py` — reads the connection DSN and executes the catalog queries.

## Configuration

`CATALOG_DB_DSN` is required at import time and supplies the PostgreSQL connection string. No
other database configuration is declared in the module.

## Failure modes

Missing `CATALOG_DB_DSN` fails during import. Connection failures, cursor failures, and SQL errors
propagate to the caller. The module contains no logging, metrics, retry, or alert configuration.
