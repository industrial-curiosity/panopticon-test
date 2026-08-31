---
type: component
---

# queue

## Responsibility

The `queue` component sends fulfillment tasks to, receives tasks from, and deletes tasks on the
`fulfillment-queue` SQS interface. Messages contain an order ID and item list encoded as JSON.

## Interfaces

The component both produces and consumes `fulfillment-queue`. See
[interfaces.md](../interfaces.md) for the indexed entry.

## Key modules

- `inventory/queue/fulfillment_queue.py` — creates the SQS client, sends and receives messages,
  and deletes a message by receipt handle.

## Configuration

`FULFILLMENT_QUEUE_URL` is required at import time and supplies the SQS queue URL. The receive
helper requests up to ten messages and waits up to five seconds for messages when called with its
default arguments.

## Failure modes

Missing `FULFILLMENT_QUEUE_URL` fails during import. Boto3 client and SQS operation failures
propagate to the caller. No logging, metrics, retry policy, or alert configuration is declared.
