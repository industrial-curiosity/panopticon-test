# Panopticon documentation changelog

## 2026-07-26

- `README.md`: removed nonexistent-file references and clarified that the repository has no visible application bootstrap.
- `docs/architecture.md`: replaced unsupported component-to-component flows with the relationships actually evidenced by the source modules.
- `docs/components/queue.md` and `docs/components/storage.md`: removed nonexistent infrastructure-file references and corrected the unproven ownership claims.
- `docs/components/clients.md`: aligned configuration and failure-mode wording with the TypeScript client implementations.
- `ts-order-service.md`: replaced obsolete fixture claims about absent infrastructure and sibling repositories with the checked-in interface evidence.

## 2026-08-09

- `README.md`: the repository-structure tree omitted `infra/`; added the `infra/` declarations for the consumed services, S3 bucket, and SQS queue.
- `ts-order-service.md`: claimed the repository contains no `infra/` directory and that the S3/SQS resources have no declared ownership; `infra/` has been tracked since the initial commit and declares both resources, so the fixture description was corrected and the ownership sentence updated.
- `docs/components/queue.md` and `docs/components/storage.md`: the previous pass stripped the ownership claims for `order-processing-queue` and `order-attachments-bucket` as "unproven", but `infra/sqs-queues.yaml` and `infra/s3-buckets.yaml` (tracked since the initial commit) declare both resources and the instance shard records this repo as their owner; restored ownership and added the infra files to the key-module lists.
- `docs/components/api.md`: the webhook receivers in `src/api/routes/webhooks.ts` were described but not indexed; they produce the `stripe-payments` and `shipping-provider-api` webhook interfaces owned by the api component, and `panopticon-interface` hints were added to that file.
- `docs/interfaces.md`: regenerated from the updated local index, which now includes the webhook producers, the `infra/*.yaml` source files, and the storage/queue ownership of the S3 bucket and SQS queue.
- `panopticon/index.json`: reconciled with the instance's compiled interface index — added the `stripe-payments` and `shipping-provider-api` webhook producers, the `infra/*.yaml` source files, and ownership of `order-attachments-bucket` (storage) and `order-processing-queue` (queue).
