# panopticon-test-child-a — operations

## Running locally

Prerequisites: Python 3.11+.

```bash
pip install -e .
```

This installs the `inventory` package and its dependencies (`fastapi`, `uvicorn`, `boto3`,
`confluent-kafka`, `psycopg2-binary`, `httpx`, `pydantic` — see `pyproject.toml`). No seed/setup
steps exist in this repo.

To run the API (FastAPI app defined in `inventory/api/routes.py` as `app`), all required
environment variables from [Required configuration](#required-configuration) must be set first,
then:

```bash
uvicorn inventory.api.routes:app
```

The Kafka consumer in `inventory/events/kafka_consumer.py` has no entrypoint script in this repo
— it must be invoked manually, e.g. `python -c "from inventory.events.kafka_consumer import run; run()"`,
after setting `KAFKA_BOOTSTRAP_SERVERS`.

## Testing

No test suite exists in this repo (no `tests/` directory, no test dependency in
`pyproject.toml`).

## Deployment

Not defined in this repo. The only CI workflows present
(`.github/workflows/panopticon-*.yml`) run Panopticon's own documentation/index sync and PR
checks — they do not build, test, or deploy the `inventory` package.

## Required configuration

Each variable is read at module import time (a missing value raises `KeyError` on import of that
module), so all variables used by a given entrypoint must be set before it starts:

| Variable | Used by | Description |
| --- | --- | --- |
| `ORDERS_API_URL` | `inventory/clients/orders.py` | Base URL for the orders service REST API |
| `WAREHOUSE_ERP_URL` | `inventory/clients/erp.py` | Base URL for the on-premise warehouse ERP |
| `KAFKA_BOOTSTRAP_SERVERS` | `inventory/events/kafka_consumer.py` | Kafka bootstrap server addresses |
| `FULFILLMENT_QUEUE_URL` | `inventory/queue/fulfillment_queue.py` | SQS queue URL for fulfillment tasks |
| `INVENTORY_SNAPSHOTS_BUCKET` | `inventory/storage/snapshots.py` | S3 bucket name for daily inventory snapshots |
| `CATALOG_DB_DSN` | `inventory/db/catalog.py` | PostgreSQL DSN for the product catalog RDS instance |

No secret names beyond the above are evidenced in the repo (values are read from environment
variables, not from a secrets file).

## Observability

No logging, metrics, dashboards, or alerting configuration is present in this repo — none of the
modules import a logging or metrics library, and no dashboard/alert definitions exist in the
repo.
