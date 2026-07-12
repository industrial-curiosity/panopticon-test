# clients

## Responsibility

Owns outbound REST integration code for three external services: an inventory service, Stripe,
and a shipping provider. Each file exports plain async functions wrapping `fetch` (inventory,
shipping) or the `stripe` SDK (payments) — there is no shared HTTP client, retry logic, or base
class among them. Out of scope: nothing in this repo currently calls any function in this
directory (no route handler or worker wires these in).

## Interfaces

- Consumes `inventory-api`, `stripe-payments`, and `shipping-provider-api` (all `rest`), extracted
  by the LLM fallback pass. Each is declared in `infra/services.yaml` (carrying its own
  `# panopticon-interface <name>` hint) and consumed again by this component's own client file
  (`inventory.ts`, `stripe.ts`, `shipping.ts`), matched to the same interface by its
  environment-variable base URL (`INVENTORY_API_URL`, `SHIPPING_API_URL`) or, for Stripe, the SDK
  it wraps. All three have `owner: null` in the index — they are external services this repo does
  not own. See [interfaces.md](../interfaces.md).

## Key modules

- `src/clients/inventory.ts` — `checkInventory`, `reserveInventory`, `releaseInventory` against
  `${INVENTORY_API_URL}/inventory/...`.
- `src/clients/stripe.ts` — `createPaymentIntent`, `confirmPayment`, `refundPayment` via the
  `stripe` npm SDK (`apiVersion: '2023-10-16'`).
- `src/clients/shipping.ts` — `getQuotes`, `createShipment`, `trackShipment` against
  `${SHIPPING_API_URL}/...`.

## Configuration

- `INVENTORY_API_URL` — required (non-null-asserted); inventory service base URL.
- `STRIPE_SECRET_KEY` — required; Stripe secret API key.
- `SHIPPING_API_URL` — required (non-null-asserted); shipping provider base URL.

## Failure modes

`inventory.ts` and `shipping.ts` throw an `Error` with the HTTP status on any non-OK response
(e.g. `Inventory check failed: 500`); callers must catch these explicitly since none of these
functions retry or degrade gracefully. `stripe.ts` has no explicit error handling and surfaces
whatever the `stripe` SDK throws directly (typically a `Stripe.errors.StripeError` subtype).
