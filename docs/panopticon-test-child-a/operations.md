---
type: component
---

# panopticon-test-child-a — operations

<!-- panopticon-analysis-scope:start -->
## Panopticon analysis scope

Panopticon excludes illustrative material from interface, dependency, and doc-drift analysis.

### Excluded directories currently in this repository

- None currently detected.

Directories whose exact path component is one of `examples`, `samples`, `fixtures`, `testdata`, `demos`, `scaffolding`, `demo`, `scaffold` are excluded case-insensitively.
Similar production paths, such as `src/sample-service`, remain in scope.

Use `panopticon-ignore file` in one of a file's first five nonblank lines to exclude the whole file. Use `panopticon-ignore declaration` on a declaration line or the line immediately before it to exclude only that declaration.
<!-- panopticon-analysis-scope:end -->

## Running locally

The repository has no application bootstrap. The two FastAPI applications can be started
individually with `uvicorn inventory.api.routes:app` for the inventory routes or
`uvicorn inventory.api.orders_routes:app` for the orders routes. The integration modules require
the environment variables listed below when they are imported or used.

## Testing

No test suite or test runner configuration is present in this repository. No automated pass
criteria can be established from the checked-in files.

## Deployment

No deployment manifests or application deployment workflow are present. The deployment owner,
target environments, approvals, and rollback procedure cannot be determined from this checkout.

## Required configuration

The source reads these environment variables:

- `ORDERS_API_URL` — orders API base URL.
- `ORDER_PROCESSING_URL` — order-processing service base URL.
- `WAREHOUSE_ERP_URL` — warehouse ERP base URL.
- `CATALOG_DB_DSN` — PostgreSQL catalog connection string.
- `KAFKA_BOOTSTRAP_SERVERS` — Kafka bootstrap servers.
- `FULFILLMENT_QUEUE_URL` — SQS fulfillment queue URL.
- `INVENTORY_SNAPSHOTS_BUCKET` — S3 inventory snapshot bucket.

AWS credentials and region are resolved by boto3 rather than by configuration code in this
repository. No secret values are committed here.

## Observability

The source contains no logging, metrics, dashboards, or alert definitions. HTTP failures are
raised by `httpx`, database and AWS failures propagate from their clients, and non-EOF Kafka
errors raise from the consumer loop. Start diagnosis at the caller and the relevant external
system because this repository does not add an observability layer.
