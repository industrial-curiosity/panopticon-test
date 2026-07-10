# Panopticon changelog

## 2026-07-10 — doc regeneration after `infra/` addition

**Found:** `panopticon/index.json` and all four doc layers were generated before the `add infra`
commit added `infra/s3-buckets.yaml`, `infra/services.yaml`, and `infra/sqs-queues.yaml` — each
already carrying `# panopticon-interface <name>` hints. The index still had only the two
deterministic-parser interfaces (`orders-api`, `order-events`), and `docs/architecture.md`,
`docs/operations.md`, and `docs/components/{worker,storage,clients}.md` all asserted (now
incorrectly) that the SQS queue, S3 bucket, and external service dependencies had no config file a
parser or LLM-fallback pass could extract from.

**Resolved:** ran LLM-fallback extraction over the three `infra/*.yaml` files, honoring their
existing hints, and added five interfaces to `panopticon/index.json`:
`order-attachments-bucket` (s3, owner component `storage`), `order-processing-queue` (sqs, owner
component `worker`), and `inventory-api` / `stripe-payments` / `shipping-provider-api` (rest,
`owner: null` — external). Re-rendered `docs/interfaces.md` from the updated index and revised the
architecture, operations, and affected component docs to describe the now-indexed interfaces
instead of claiming they weren't extractable.

**Judgment call:** the repo's own `ts-order-service.md` fixture doc illustrates this same
extraction with the SQS-owning component named `queue`; this run instead used `worker`, the
component name already established by the real `docs/components/worker.md` (which documents the
same `src/queue/*.ts` files), to avoid introducing a second, docless component for the same source.
If `queue` was actually intended, rename the component in the index and split/rename the doc
accordingly.
