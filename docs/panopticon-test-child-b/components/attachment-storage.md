---
type: component
---

# attachment-storage

## Responsibility

This component stores order attachments in S3, retrieves objects, creates signed download URLs, and deletes objects. The bucket is declared as `order-attachments-bucket` in the infrastructure configuration.

Object authorization, retention enforcement, and bucket deployment are outside the committed TypeScript module.

## Interfaces

This component owns and consumes [`order-attachments-bucket`](../interfaces.md#order-attachments-bucket).

## Key modules

- `src/storage/attachments.ts` — implements S3 put, get URL, and delete operations.
- `infra/s3-buckets.yaml` — declares the bucket name, versioning setting, and lifecycle expiration.

## Configuration

- `ORDER_ATTACHMENTS_BUCKET` — required bucket name.
- `AWS_REGION` — AWS region; the client defaults to `us-east-1` when unset.
- AWS SDK credential-provider configuration — required by the runtime environment; no credential values are stored here.

## Failure modes

S3 operation failures reject the returned promises and are not caught in this module. Signed URL generation also rejects when the SDK cannot prepare the request. No local logs, metrics, or alerts are configured.
