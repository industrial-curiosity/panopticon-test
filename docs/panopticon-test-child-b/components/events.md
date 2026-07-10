# events

## Responsibility

Owns publishing order lifecycle events (`order.created`, `order.updated`, `order.cancelled`,
`order.shipped`, `order.delivered`) to Kafka. Defined by `src/events/kafka-topics.yaml` (topic
config) and `src/events/producer.ts` (publish function). Out of scope: no code in this repo
currently calls `publishOrderEvent` — nothing in `api` or elsewhere emits events at runtime.

## Interfaces

- Produces `order-events` (`kafka`), owned by this repo. See [interfaces.md](../interfaces.md).

## Key modules

- `src/events/kafka-topics.yaml` — declares the `order-events` topic: 12 partitions,
  replication factor 3, 7-day retention (`retention.ms: 604800000`), `cleanup.policy: delete`.
- `src/events/producer.ts` — `publishOrderEvent(event: OrderEvent): Promise<void>` connects a
  `kafkajs` producer and sends a keyed message (key = `orderId`) to the `order-events` topic.

## Configuration

- `KAFKA_BROKERS` — comma-separated broker list; defaults to `localhost:9092` when unset
  (`src/events/producer.ts`).

## Failure modes

`publishOrderEvent` calls `producer.connect()` on every invocation with no reuse or reconnect
logic, and does not catch errors from `connect()` or `send()` — a broker-connectivity failure
propagates as an unhandled promise rejection to whatever calls this function. Since nothing
currently calls it, this failure path is not exercised in the present codebase.
