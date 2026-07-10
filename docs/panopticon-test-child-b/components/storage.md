# storage

## Responsibility

Owns storage of order attachments (e.g. receipts, uploads) in S3: upload, generate a
time-limited signed URL, and delete. Out of scope: nothing in this repo currently calls
`uploadAttachment`, `getAttachmentUrl`, or `deleteAttachment` — no route handler wires this in.

## Interfaces

- Owns `order-attachments-bucket` (`s3`), extracted by the LLM fallback pass from
  `infra/s3-buckets.yaml` (the bucket's declaration, carrying the
  `# panopticon-interface order-attachments-bucket` hint). `src/storage/attachments.ts` itself only
  references the bucket via the `ORDER_ATTACHMENTS_BUCKET` environment variable, with no
  declaration a parser or LLM pass can extract a name from — the index entry is grounded in the
  `infra/` config, not the TypeScript. See [interfaces.md](../interfaces.md).

## Key modules

- `src/storage/attachments.ts` — `uploadAttachment(orderId, fileName, body, contentType)` (key
  pattern `orders/{orderId}/{fileName}`), `getAttachmentUrl(key, expiresIn = 3600)` (signed URL
  via `@aws-sdk/s3-request-presigner`), `deleteAttachment(key)`. Wraps `@aws-sdk/client-s3`.

## Configuration

- `ORDER_ATTACHMENTS_BUCKET` — required (non-null-asserted); the S3 bucket name.
- `AWS_REGION` — defaults to `us-east-1` when unset.

## Failure modes

None of the three functions catch or wrap S3 client errors — an `S3Client.send` failure (e.g.
missing bucket, permission denial, network error) propagates directly to the caller as whatever
error the AWS SDK throws. `uploadAttachment` and `deleteAttachment` have no retry logic.
