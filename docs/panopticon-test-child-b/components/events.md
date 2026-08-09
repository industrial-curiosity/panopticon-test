# events

## Responsibility

The events component declares the `order-events` Kafka topic and publishes order lifecycle event payloads to it. It does not consume Kafka messages.

## Interfaces

This component produces the owned `order-events` Kafka interface, declared in `src/events/kafka-topics.yaml` and published by `src/events/producer.ts`. See [interfaces.md](../interfaces.md) for its indexed source files.

## Key modules

- `src/events/kafka-topics.yaml` — topic declaration with partition count, replication factor, and retention policy.
- `src/events/producer.ts` — Kafka producer and `OrderEvent` payload type; publishes `order.created`, `order.updated`, `order.cancelled`, `order.shipped`, and `order.delivered` events.

## Configuration

`KAFKA_BROKERS` supplies a comma-separated broker list; it defaults to `localhost:9092` when unset.

## Failure modes

Broker connection or send failures reject `publishOrderEvent`. The producer connects on every publish call in the visible implementation and never disconnects, so unavailable brokers directly prevent publication and each call incurs a new connection.
