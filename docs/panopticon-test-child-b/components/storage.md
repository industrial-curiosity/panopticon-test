# storage

## Responsibility

The storage component declares the `order-attachments-bucket` S3 bucket in `infra/s3-buckets.yaml` and manages order attachment objects in it: uploading objects, producing signed read URLs, and deleting objects by key.

## Interfaces

This component owns and both produces and consumes `order-attachments-bucket` (S3): `infra/s3-buckets.yaml` declares the bucket and `src/storage/attachments.ts` uses it. See [interfaces.md](../interfaces.md) for the indexed source files.

## Key modules

- `infra/s3-buckets.yaml` — bucket declaration with versioning and lifecycle settings.
- `src/storage/attachments.ts` — `uploadAttachment`, `getAttachmentUrl`, and `deleteAttachment` via the S3 SDK and request presigner.

## Configuration

`ORDER_ATTACHMENTS_BUCKET` is required. `AWS_REGION` selects the S3 region and defaults to `us-east-1`.

## Failure modes

S3 client errors reject the attachment operations. Missing bucket or region configuration prevents operations from targeting the intended storage location. Signed URLs default to a one-hour expiry when no explicit lifetime is supplied.
