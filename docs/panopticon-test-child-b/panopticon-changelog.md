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

## 2026-07-12 — extended LLM-fallback extraction to `.ts` files; fixture doc updated to match

**Found:** none of the `.ts` source files (`src/clients/*.ts`, `src/api/routes/*.ts`,
`src/queue/*.ts`, `src/storage/attachments.ts`, `src/events/producer.ts`) appeared as
`source_files` anywhere in `panopticon/index.json`, even though each one clearly references an
already-indexed interface — by a shared environment-variable name with the corresponding
`infra/*.yaml` config (`INVENTORY_API_URL`, `SHIPPING_API_URL`, `ORDER_PROCESSING_QUEUE_URL`,
`ORDER_ATTACHMENTS_BUCKET`), by topic/route identity for the two deterministic-parser interfaces,
or by SDK identity for Stripe. Two webhook-receiving routes in `src/api/routes/webhooks.ts`
(`POST /stripe`, `POST /shipping`) were not represented in the index at all. Separately,
`order-events` and `orders-api` had `owner.component` set to the repo name itself
(`panopticon-test-child-b`) rather than their real owning components. The repo's own
`ts-order-service.md` fixture doc asserted this omission was by design (*"`.ts` source files are
not in the LLM fallback suffix set"*) and showed the repo-name component fallback as expected
parser behavior — directly contradicting what the evidence in the `.ts` files supported.

**Resolved:** confirmed with the user that the actual repo/index state, not the fixture doc, is
ground truth going forward. Added the `.ts` files as producer/consumer evidence on their matching
existing interfaces, added two new `webhook`-type entries (`stripe-payments`,
`shipping-provider-api`) owned by `api` for the webhook receivers, added
`# panopticon-interface` hints above each route in `webhooks.ts`, corrected `order-events` and
`orders-api` `owner.component` to `events` and `api`, re-rendered `docs/interfaces.md`, and revised
`docs/architecture.md` (including adding the previously-missing `## Architecture diagram` section
required by `panopticon.docs.validate_docs`) and the `api`/`clients`/`events`/`storage`/`worker`
component docs to describe the current index instead of the old "no name a parser or LLM pass can
extract" claim. Rewrote `ts-order-service.md` in full to match: `.ts` evidence is now documented as
included, both webhook entries are documented, and the expected `panopticon/index.json` block was
updated to the real current index.

**Judgment call:** this reverses the previous run's implicit design constraint (also reflected in
`ts-order-service.md`) that `.ts` files carry no extractable interface evidence. The correlation
used to justify extraction — an exact shared environment-variable name, or, for Stripe, SDK
identity — is concrete rather than inferred, so this is treated as a legitimate extension of
extraction coverage rather than a guess. If a future run wants to restore the `.ts`-exclusion
design, both the index entries added here and this fixture doc's description of them need to be
reverted together.
