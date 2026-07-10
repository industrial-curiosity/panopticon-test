# queue

## Responsibility

Owns the `fulfillment-queue` SQS queue used to hand off async fulfillment tasks: enqueueing a
task, polling for tasks, and deleting a task once processed. Not called from any other component
in this repo currently (see [architecture.md](../architecture.md#data-flow)).

## Interfaces

- **`fulfillment-queue`** (`sqs`) — owned/produced and consumed here (this repo both enqueues and
  polls/deletes its own queue). See [interfaces.md](../interfaces.md#fulfillment-queue).

## Key modules

- `inventory/queue/fulfillment_queue.py` — `enqueue_fulfillment_task(order_id, items)`,
  `poll_fulfillment_tasks(max_messages=10)`, `delete_fulfillment_task(receipt_handle)`, all
  against a single SQS queue via a module-level `boto3` client.

## Configuration

- `FULFILLMENT_QUEUE_URL` — SQS queue URL for fulfillment tasks. Required (read at import time;
  missing value raises `KeyError` on import).

## Failure modes

No error handling around the `boto3` SQS calls — any AWS/SQS error (throttling, permissions,
network) propagates directly to the caller. `poll_fulfillment_tasks` blocks for up to 5 seconds
(`WaitTimeSeconds=5`) per call when the queue is empty.
