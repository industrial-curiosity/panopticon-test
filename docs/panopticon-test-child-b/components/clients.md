# clients

## Responsibility

The clients component calls the inventory, Stripe, and shipping services for order-related work. It does not own the remote APIs it uses; `infra/services.yaml` declares them as consumed services.

## Interfaces

This component consumes the `inventory-api`, `stripe-payments` (REST), and `shipping-provider-api` (REST) interfaces via `infra/services.yaml` and the respective client modules. Their indexed ownership and source evidence are in [interfaces.md](../interfaces.md).

## Key modules

- `src/clients/inventory.ts` — `checkInventory`, `reserveInventory`, and `releaseInventory` calls against `inventory-api`.
- `src/clients/stripe.ts` — `createPaymentIntent`, `confirmPayment`, and `refundPayment` against `stripe-payments` using the Stripe SDK.
- `src/clients/shipping.ts` — `getQuotes`, `createShipment`, and `trackShipment` against `shipping-provider-api`.
- `infra/services.yaml` — declares the consumed `inventory`, `stripe`, and `shipping` services with their base URLs.

## Configuration

`INVENTORY_API_URL`, `STRIPE_SECRET_KEY`, and `SHIPPING_API_URL` are read by the respective client modules. The source uses non-null assertions and provides no defaults or runtime validation, so each is effectively required for the corresponding client to work.

## Failure modes

Inventory and shipping functions throw when the remote HTTP response is unsuccessful. Stripe client calls surface SDK errors. Missing or invalid environment values make the corresponding remote operation fail, either at request time or with an unusable base URL or secret.
