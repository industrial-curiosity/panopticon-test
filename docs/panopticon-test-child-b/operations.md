---
type: operations
---

# panopticon-test-child-b — operations

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

Install the declared Node.js dependencies with `npm install`. `npm run build` compiles the TypeScript modules into `dist/`; it does not create an application entry point because `src/index.ts` is absent. `npm run worker` starts the SQS long-poll worker after `ORDER_PROCESSING_QUEUE_URL`, AWS credentials, and the required region are configured.

The `npm run dev` and `npm start` scripts reference `src/index.ts` and `dist/index.js`, respectively. Those entry points are not committed, so these scripts cannot start the HTTP modules in this repository snapshot.

## Testing

No test files or `test` script are committed. Use `npm run build` as the available static TypeScript check after installing dependencies; success means the compiler exits with status 0.

## Deployment

This repository contains no deployment workflow or release configuration. Deployment of the HTTP routes, worker, Kafka topic, SQS queue, and S3 bucket must be provided by an external platform or repository.

## Required configuration

- `INVENTORY_API_URL` — base URL for inventory calls.
- `SHIPPING_API_URL` — base URL for shipping calls.
- `STRIPE_SECRET_KEY` — Stripe credential.
- `KAFKA_BROKERS` — comma-separated Kafka brokers; defaults to `localhost:9092`.
- `ORDER_PROCESSING_QUEUE_URL` — SQS queue URL.
- `ORDER_ATTACHMENTS_BUCKET` — S3 bucket name.
- `AWS_REGION` — AWS region; defaults to `us-east-1`.
- AWS SDK credentials — supplied by the runtime environment's credential provider; values are not stored in this repository.

## Observability

The worker writes startup, per-action, and processing-failure messages to stdout/stderr. The committed HTTP, Kafka, client, and S3 modules define no metrics, tracing, dashboards, or alert rules. Any runtime platform that captures process output is the only observability surface evidenced in this repository.
