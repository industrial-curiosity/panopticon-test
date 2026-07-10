# api

## Responsibility

Owns the order-management HTTP surface: listing, creating, retrieving, updating, and cancelling
orders, plus stub webhook receivers for Stripe and shipping callbacks. Defined by
`src/api/openapi.yaml` (the contract) and implemented by the Express routers in
`src/api/routes/`. Out of scope: the route handlers currently return hardcoded or pass-through
data and do not call the `clients`, `events`, or `storage` components — request-time integration
with inventory, payments, shipping, event publishing, or attachment storage is not implemented.

## Interfaces

- Produces `orders-api` (`rest`), owned by this repo. See [interfaces.md](../interfaces.md).

## Key modules

- `src/api/openapi.yaml` — the OpenAPI 3.0 contract: `Order`, `OrderItem`,
  `CreateOrderRequest`, `UpdateOrderRequest` schemas and the `/orders` path family.
- `src/api/routes/orders.ts` — Express router implementing `GET/POST /orders`,
  `GET/PATCH /orders/:id`, `POST /orders/:id/cancel`. Handlers return stub data (e.g. `POST /`
  always returns `status: 'pending'` with no persistence).
- `src/api/routes/webhooks.ts` — `POST /stripe` and `POST /shipping` webhook receivers; both
  currently just acknowledge receipt (`{ received: true }`) without processing the payload.

## Configuration

None read directly by these route files — no environment variables or flags appear in
`src/api/routes/*` or `src/api/openapi.yaml`.

## Failure modes

No error handling, validation, or persistence exists in the current route implementations, so
there is no observable failure mode beyond default Express error handling — request bodies are
not validated against the OpenAPI schema, and no data is retained between requests. There is also
no assembled Express app: `package.json`'s `dev`/`start` scripts point at `src/index.ts` and
`dist/index.js`, neither of which exists, so this component cannot currently be run or fail at
runtime.
