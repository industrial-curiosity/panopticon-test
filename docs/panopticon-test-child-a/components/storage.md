# storage

## Responsibility

Owns the `inventory-snapshots` S3 bucket used for daily inventory snapshots: uploading a
snapshot, downloading a snapshot for a given date, and listing available snapshots. Intended for
audit and recovery. Not called from any other component in this repo currently.

## Interfaces

- **`inventory-snapshots`** (`s3`) — owned/produced and consumed here (this repo both writes and
  reads back its own snapshots). See [interfaces.md](../interfaces.md#inventory-snapshots).

## Key modules

- `inventory/storage/snapshots.py` — `upload_snapshot(snapshot_date, data)`,
  `download_snapshot(snapshot_date)`, `list_snapshots()`, all against a single S3 bucket via a
  module-level `boto3` client. Objects are keyed `snapshots/{date}/inventory.json`.

## Configuration

- `INVENTORY_SNAPSHOTS_BUCKET` — S3 bucket name for daily inventory snapshots. Required (read at
  import time; missing value raises `KeyError` on import).

## Failure modes

No error handling around the `boto3` S3 calls — any AWS/S3 error (missing object, permissions,
network) propagates directly to the caller. `download_snapshot` raises if no snapshot exists for
the requested date.
