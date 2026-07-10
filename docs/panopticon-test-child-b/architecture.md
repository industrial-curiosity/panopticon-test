# panopticon-test-child-b — architecture overview

## Purpose

`panopticon-test-child-b` is a TypeScript order-management codebase: order CRUD, an order-events
Kafka topic, an SQS-backed job queue for order processing, S3 storage for order attachments, and
REST clients for an inventory service, Stripe, and a shipping provider. Per `ts-order-service.md`,
this repo also serves as a Panopticon test fixture — its structure exists to exercise deterministic
parsers (REST/OpenAPI, Kafka) and LLM-fallback extraction against a real TypeScript layout.

## Components

- [api](components/api.md) — HTTP route handlers and the OpenAPI spec for order management
- [events](components/events.md) — Kafka producer for order lifecycle events
- [worker](components/worker.md) — long-running SQS consumer that processes order jobs
- [clients](components/clients.md) — outbound REST clients to inventory, Stripe, and shipping
- [storage](components/storage.md) — S3-backed order attachment storage

## Data flow

The modules above are not wired together in code: `package.json` declares a `dev` script
(`ts-node src/index.ts`) and a `main` entry (`dist/index.js`) that would presumably assemble the
Express app and mount `src/api/routes/*`, but `src/index.ts` does not exist anywhere in the repo
or its git history, and no other file imports `src/clients/*`, `src/events/producer.ts`, or
`src/storage/attachments.ts`. `src/api/routes/orders.ts` and `webhooks.ts` currently return
hardcoded/stub responses and do not call any of those modules either.

The one real wiring that does exist: `src/queue/worker.ts` imports `receiveOrders` and
`deleteMessage` from `src/queue/processor.ts` and runs a long-poll loop that logs each job action
(`process`, `fulfill`, `cancel`) without calling the inventory, Stripe, shipping, events, or
storage modules.

Each module's intended role, as declared by its own code:

1. `api` exposes `orders-api` (`GET/POST /orders`, `GET/PATCH /orders/:id`,
   `POST /orders/:id/cancel`) per `src/api/openapi.yaml`.
2. `events` publishes to the `order-events` Kafka topic via `publishOrderEvent`.
3. `worker` long-polls an SQS queue (`ORDER_PROCESSING_QUEUE_URL`) for `OrderJob` messages and
   processes them.
4. `clients` and `storage` expose reusable functions (inventory checks/reservations, payment
   intents, shipping quotes/shipments, S3 attachment upload/URL/delete) that no current caller
   invokes.

## Dependencies

- **Kafka** (`KAFKA_BROKERS`) — required to publish to `order-events`; see
  [interfaces.md](interfaces.md).
- **AWS SQS** (`ORDER_PROCESSING_QUEUE_URL`, `AWS_REGION`) — the `worker` component's job queue,
  declared in `infra/sqs-queues.yaml` and indexed as `order-processing-queue`; see
  [interfaces.md](interfaces.md) and [components/worker.md](components/worker.md).
- **AWS S3** (`ORDER_ATTACHMENTS_BUCKET`, `AWS_REGION`) — attachment storage used by `storage`,
  declared in `infra/s3-buckets.yaml` and indexed as `order-attachments-bucket`; see
  [interfaces.md](interfaces.md) and [components/storage.md](components/storage.md).
- **Inventory service** (`INVENTORY_API_URL`) — external REST dependency consumed by `clients`,
  declared in `infra/services.yaml` and indexed as `inventory-api` (`owner: null` — owned outside
  this repo); see [interfaces.md](interfaces.md).
- **Stripe** (`STRIPE_SECRET_KEY`) — external payments API consumed by `clients` via the `stripe`
  npm package, declared in `infra/services.yaml` and indexed as `stripe-payments` (`owner: null` —
  third-party); see [interfaces.md](interfaces.md).
- **Shipping provider** (`SHIPPING_API_URL`) — external REST dependency consumed by `clients`,
  declared in `infra/services.yaml` and indexed as `shipping-provider-api` (`owner: null` —
  third-party); see [interfaces.md](interfaces.md).
