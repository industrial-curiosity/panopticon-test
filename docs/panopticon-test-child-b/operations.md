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

Install the declared Node.js dependencies with `npm install`. Use `npm run build` to compile TypeScript with `tsc`, and `npm run worker` to start the SQS long-poll worker via `ts-node src/queue/worker.ts`.

The `dev` script runs `ts-node src/index.ts` and `start` runs `node dist/index.js`, but `src/index.ts` does not exist in the repository, so the build produces no `dist/` and neither command can be verified from the checked-in source.

## Testing

No test scripts or test suites are declared in `package.json`. TypeScript compilation via `npm run build` is the available repository-level verification command.

## Deployment

No deployment pipeline, environment promotion process, approval flow, or rollback procedure is present in the repository. The `infra/` YAML files declare interface-related resources only: the consumed services, the S3 bucket, and the SQS queue.

## Required configuration

Set `INVENTORY_API_URL`, `STRIPE_SECRET_KEY`, `SHIPPING_API_URL`, `ORDER_PROCESSING_QUEUE_URL`, and `ORDER_ATTACHMENTS_BUCKET` for the applicable clients. Set `KAFKA_BROKERS` to override its local default, and set `AWS_REGION` to override the default `us-east-1` used by SQS and S3. The configuration comes from environment variables supplied at runtime; no configuration files or secret references are committed.

## Observability

The worker writes startup, processing, and per-job failure messages to standard output or error. No metrics, dashboards, tracing, or alert definitions are visible in the repository.
