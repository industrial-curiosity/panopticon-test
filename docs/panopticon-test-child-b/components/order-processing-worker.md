---
type: component
---

# order-processing-worker

## Responsibility

This component sends and receives order jobs through the `order-processing-queue` SQS queue and runs the long-poll worker loop. The worker handles `process`, `fulfill`, and `cancel` job actions with console output.

The committed worker contains no deployment definition, graceful-shutdown handling, or application bootstrap beyond its exported runner.

## Interfaces

This component owns and consumes [`order-processing-queue`](../interfaces.md#order-processing-queue).

## Key modules

- `src/queue/processor.ts` — configures the SQS client and implements enqueue, receive, and delete operations.
- `src/queue/worker.ts` — polls for jobs, processes each action, and deletes successful messages.
- `infra/sqs-queues.yaml` — declares the queue and its visibility/long-poll settings.

## Configuration

- `ORDER_PROCESSING_QUEUE_URL` — required SQS queue URL.
- `AWS_REGION` — AWS region; the client defaults to `us-east-1` when unset.
- AWS SDK credential-provider configuration — required by the runtime environment; no credential values are stored here.

## Failure modes

Receive failures occur outside the worker's per-message `try` block and can terminate the loop. Processing or deletion failures are logged to stderr and leave the message undeleted by this code. Invalid message JSON can fail before the per-message handling block receives a job.
