---
type: component
---

# events

## Responsibility

The `events` component consumes the `order-events` Kafka topic. It creates a consumer in the
`inventory-service` group, polls continuously, and dispatches `order.created` and
`order.cancelled` messages to local handlers.

## Interfaces

The component consumes `order-events`. See [interfaces.md](../interfaces.md) for the indexed entry.

## Key modules

- `inventory/events/kafka_consumer.py` — configures the Kafka consumer, subscribes to the topic,
  polls messages, and dispatches recognized event types.

## Configuration

- `KAFKA_BOOTSTRAP_SERVERS` is required at import time and supplies the Kafka bootstrap servers.
- The topic name is the source constant `order-events`.
- The consumer group is the source constant `inventory-service`.
- Polling uses a one-second timeout and starts from the earliest offset when no offset exists.

## Failure modes

Missing `KAFKA_BOOTSTRAP_SERVERS` fails during import. Kafka errors other than partition EOF raise
an exception and end the loop; the consumer is closed in the `finally` block. The two event
handlers currently have no implementation. No logging, metrics, or alert configuration is present.
