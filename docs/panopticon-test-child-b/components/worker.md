# worker

## Responsibility

Owns background processing of order jobs: long-polls an SQS queue, dispatches each job by
`action` (`process`, `fulfill`, `cancel`), and deletes the message on success. This is the one
component in the repo with a working runnable entry point (`npm run worker`). Out of scope: job
handling is currently logging-only (`console.log`) — it does not call `clients`, `events`, or
`storage` to actually reserve inventory, charge payments, arrange shipping, or publish events.

## Interfaces

- Owns `order-processing-queue` (`sqs`), extracted by the LLM fallback pass. Declared in
  `infra/sqs-queues.yaml` (carrying the `# panopticon-interface order-processing-queue` hint) and
  referenced again by `src/queue/processor.ts` and `src/queue/worker.ts` via the
  `ORDER_PROCESSING_QUEUE_URL` environment variable, matching the same hinted queue.
  `processor.ts` is recorded as both producer (`enqueueOrder`) and consumer (`receiveOrders`);
  `worker.ts` is recorded as consumer (it drives the receive/delete loop via `processor.ts`). See
  [interfaces.md](../interfaces.md).

## Key modules

- `src/queue/processor.ts` — `enqueueOrder`, `receiveOrders` (20s long-poll,
  `MaxNumberOfMessages` configurable), and `deleteMessage`, wrapping `@aws-sdk/client-sqs`.
- `src/queue/worker.ts` — `runWorker()`: an infinite loop that calls `receiveOrders`, processes
  each `OrderJob` by `action`, deletes the message on success, and logs (but does not rethrow)
  per-job errors.

## Configuration

- `ORDER_PROCESSING_QUEUE_URL` — required (non-null-asserted); the SQS queue URL.
- `AWS_REGION` — defaults to `us-east-1` when unset.

## Failure modes

A per-job processing error is caught and logged in `runWorker`'s loop (`Failed to process job for
order ${job.orderId}`), and the message is left un-deleted so SQS will redeliver it — there is no
dead-letter or retry-limit handling in this code, so a message that always fails to process will
loop indefinitely. A failure in `receiveOrders` itself (e.g. SQS unreachable) is not caught and
would terminate the worker process.
