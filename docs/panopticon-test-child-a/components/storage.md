---
type: component
---

# storage

## Responsibility

The `storage` component stores and retrieves dated inventory snapshots in the
`inventory-snapshots` S3 bucket. It uses a stable key layout under
`snapshots/{YYYY-MM-DD}/inventory.json` and can list all objects under the snapshots prefix.

## Interfaces

The component both produces and consumes `inventory-snapshots`. See
[interfaces.md](../interfaces.md) for the indexed entry.

## Key modules

- `inventory/storage/snapshots.py` — creates the S3 client, writes and reads JSON snapshots, and
  lists snapshot keys.

## Configuration

`INVENTORY_SNAPSHOTS_BUCKET` is required at import time and supplies the S3 bucket name. AWS
credential and region resolution is delegated to the standard boto3 client configuration and is
not specified in this repository.

## Failure modes

Missing `INVENTORY_SNAPSHOTS_BUCKET` fails during import. S3 client and object operation failures
propagate to the caller. No logging, metrics, retry policy, or alert configuration is declared.
