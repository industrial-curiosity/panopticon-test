---
type: component
---

# order-integrations

## Responsibility

This component provides client modules for inventory availability/reservation, shipping quotes/shipments/tracking, and Stripe payment intents/refunds. It consumes external systems and does not own their interfaces.

Business orchestration and the caller that coordinates these clients are not present in this repository.

## Interfaces

This component consumes [`inventory-api`](../interfaces.md#inventory-api), [`shipping-api`](../interfaces.md#shipping-api), and [`stripe-api`](../interfaces.md#stripe-api).

## Key modules

- `src/clients/inventory.ts` — calls inventory check, reserve, and release endpoints.
- `src/clients/shipping.ts` — calls quote, shipment creation, and tracking endpoints.
- `src/clients/stripe.ts` — calls Stripe payment-intent confirmation and refund operations through the Stripe SDK.
- `infra/services.yaml` — records the inventory, Stripe, and shipping service endpoints.

## Configuration

- `INVENTORY_API_URL` — required base URL for the inventory client.
- `SHIPPING_API_URL` — required base URL for the shipping client.
- `STRIPE_SECRET_KEY` — required Stripe secret used to create the SDK client.
- Stripe API version — fixed in code as `2023-10-16`.

## Failure modes

The HTTP clients throw on non-success responses. Stripe SDK failures reject the returned promise. No retry, timeout, circuit-breaker, logging, or metric behavior is implemented in these modules, so callers must decide how failures propagate.
