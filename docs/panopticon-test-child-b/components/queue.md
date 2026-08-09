# queue

## Responsibility

The queue component declares the `order-processing-queue` SQS queue in `infra/sqs-queues.yaml`, enqueues order jobs with `enqueueOrder`, and runs a worker that long-polls, processes, and deletes messages. The visible worker logs process, fulfill, and cancel actions.

## Interfaces

This component owns and both produces and consumes `order-processing-queue` (SQS): `infra/sqs-queues.yaml` declares the queue, `src/queue/processor.ts` sends and receives messages, and `src/queue/worker.ts` long-polls and deletes them. See [interfaces.md](../interfaces.md) for the indexed source files.

## Key modules

- `infra/sqs-queues.yaml` — queue declaration with visibility timeout and receive-wait settings.
- `src/queue/processor.ts` — `enqueueOrder`, `receiveOrders`, and `deleteMessage` via the SQS SDK.
- `src/queue/worker.ts` — `processJob` action dispatch and the `runWorker` long-poll loop.

## Configuration

`ORDER_PROCESSING_QUEUE_URL` is required. `AWS_REGION` selects the SQS region and defaults to `us-east-1`.

## Failure modes

SQS operation failures reject the queue functions. The worker catches errors during individual job processing, logs them, and does not delete the message, so it remains in the queue for another attempt; there is no dead-letter queue or retry policy. `receiveOrders` is called outside the worker's try/catch, so a polling failure crashes the worker loop. The enqueue path sets `MessageGroupId`, which is valid only on FIFO queues, while `infra/sqs-queues.yaml` declares a standard queue.
