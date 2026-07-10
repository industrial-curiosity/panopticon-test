# panopticon-test-child-b — operations

## Running locally

`npm install` installs dependencies. Beyond that, only one of the four `package.json` scripts is
currently runnable:

- `npm run worker` (`ts-node src/queue/worker.ts`) — runs; requires `ORDER_PROCESSING_QUEUE_URL`
  (and `AWS_REGION`, `AWS` credentials via the standard SDK credential chain) to actually reach
  SQS. See [components/worker.md](components/worker.md).
- `npm run dev` (`ts-node src/index.ts`), `npm start` (`node dist/index.js`), and `npm run build`
  (`tsc`, which would emit `dist/index.js` from `src/index.ts`) all depend on `src/index.ts`,
  which does not exist anywhere in the repo or its git history. There is no assembled Express
  app anywhere in `src/` — `src/api/routes/*` define routers but nothing mounts them. These three
  scripts cannot currently run.

## Testing

No test suite exists: `package.json` defines no `test` script, and no `*.test.ts`/`*.spec.ts`
files are present anywhere in the repo.

## Deployment

Not determinable from this repo. The only workflows under `.github/workflows/` are Panopticon's
own PR/merge/close checks (`panopticon-pr.yml`, `panopticon-merge.yml`, `panopticon-pr-close.yml`)
— thin references to reusable workflows in the `industrial-curiosity/panopticon-test` instance
repo. There is no build/deploy pipeline or Dockerfile in the repo. `infra/` declares the resource
shapes this service depends on (`infra/sqs-queues.yaml` — `order-processing-queue`;
`infra/s3-buckets.yaml` — `order-attachments-bucket`; `infra/services.yaml` — the inventory,
Stripe, and shipping base URLs), but nothing in the repo provisions or deploys them — see
[architecture.md](architecture.md#dependencies) and [interfaces.md](interfaces.md).

## Required configuration

| Variable | Used by | Required |
|---|---|---|
| `INVENTORY_API_URL` | `clients` (`src/clients/inventory.ts`) | Yes (non-null-asserted) |
| `STRIPE_SECRET_KEY` | `clients` (`src/clients/stripe.ts`) | Yes |
| `SHIPPING_API_URL` | `clients` (`src/clients/shipping.ts`) | Yes (non-null-asserted) |
| `KAFKA_BROKERS` | `events` (`src/events/producer.ts`) | No — defaults to `localhost:9092` |
| `ORDER_PROCESSING_QUEUE_URL` | `worker` (`src/queue/processor.ts`) | Yes (non-null-asserted) |
| `ORDER_ATTACHMENTS_BUCKET` | `storage` (`src/storage/attachments.ts`) | Yes (non-null-asserted) |
| `AWS_REGION` | `worker`, `storage` | No — defaults to `us-east-1` |

No secrets files or config files carry these values in the repo; they are read from `process.env`
directly at each module's top level, so all are required at process-start time for the modules
that use them regardless of which npm script (if any) is run.

## Observability

Not determinable from this repo. `src/queue/worker.ts` uses `console.log`/`console.error` for
job-processing status and errors; no structured logging, metrics, dashboards, or alerting
configuration is present anywhere in the codebase.
