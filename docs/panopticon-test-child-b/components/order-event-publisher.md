---
type: component
---

# order-event-publisher

## Responsibility

This component publishes serialized order events to Kafka. It defines the `order-events` topic usage and the event types represented by the `OrderEvent` type.

Topic provisioning is represented by the infrastructure YAML; lifecycle management for the Kafka cluster is outside this repository.

## Interfaces

This component owns [`order-events`](../interfaces.md#order-events).

## Key modules

- `src/events/kafka-topics.yaml` — declares the topic name and retention settings.
- `src/events/producer.ts` — creates the Kafka client and publishes keyed JSON messages.

## Configuration

- `KAFKA_BROKERS` — comma-separated Kafka broker addresses; the module defaults to `localhost:9092` when unset.

## Failure modes

Kafka connection or send failures reject the publishing promise. The module does not catch, retry, log, or emit metrics for those failures; the caller must provide that handling.
