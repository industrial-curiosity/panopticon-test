# events

## Responsibility

Consumes the `order-events` Kafka topic and dispatches order lifecycle messages
(`order.created`, `order.cancelled`) to handler functions. The handlers themselves are currently
empty stubs — this component defines the subscription and dispatch shape, not yet the inventory
side effects. Not called from, and does not call, any other component in this repo.

## Interfaces

- **`order-events`** (`kafka`) — consumed here; owned externally by the order service, not this
  repo. See [interfaces.md](../interfaces.md#order-events).

## Key modules

- `inventory/events/kafka_consumer.py` — `build_consumer()` constructs a `confluent_kafka.Consumer`
  in group `inventory-service`; `run()` polls the `order-events` topic in a loop and calls
  `handle_order_event()`, which routes `order.created` to `_on_order_created` and
  `order.cancelled` to `_on_order_cancelled` (both currently `pass`). No entrypoint script in this
  repo invokes `run()`.

## Configuration

- `KAFKA_BOOTSTRAP_SERVERS` — Kafka bootstrap server addresses. Required (read at import time;
  missing value raises `KeyError` on import).

## Failure modes

`run()` re-raises any Kafka error other than a partition-EOF condition, which stops the consume
loop. Message deserialization (`json.loads`) is unguarded — a malformed message body raises and
propagates out of the loop. Since the handlers are stubs, no inventory-side failure mode exists
yet.
