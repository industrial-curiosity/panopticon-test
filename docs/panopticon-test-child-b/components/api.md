# api

## Responsibility

The API component defines the Orders REST contract and its route handlers, and receives inbound webhooks from Stripe and the shipping provider. It covers listing, creating, retrieving, updating, and cancelling orders, plus the `POST /stripe` and `POST /shipping` webhook receivers.

The repository does not include an application bootstrap or route mounting, so server startup and request middleware are out of scope of the visible code. The route handlers return hardcoded JSON and do not implement persistence or call other components.

## Interfaces

This component produces the owned `orders-api` REST interface (defined by `src/api/openapi.yaml` and `src/api/routes/orders.ts`) and the owned `stripe-payments` and `shipping-provider-api` webhook interfaces (defined by `src/api/routes/webhooks.ts`). It consumes no interfaces directly. Detailed index entries are in [interfaces.md](../interfaces.md).

## Key modules

- `src/api/openapi.yaml` — OpenAPI 3.0.3 contract for `orders-api`: list, create, get, update, and cancel order paths plus order schemas.
- `src/api/routes/orders.ts` — Express route handlers for the order lifecycle paths; each returns hardcoded JSON.
- `src/api/routes/webhooks.ts` — Express webhook receivers for `POST /stripe` and `POST /shipping`; each acknowledges with `{ received: true }` and reads nothing from the request.

## Configuration

No API-specific configuration is visible in these modules; no environment variables are read. Express request handling is imported, but mounting and server configuration are not present in the repository.

## Failure modes

The visible handlers always return success responses, so the 404 and 409 outcomes declared in the OpenAPI contract are never produced and the list endpoint ignores its declared query parameters. The webhook handlers acknowledge without verifying signatures or reading bodies, so malformed or spoofed webhooks are not detected. Because no bootstrap mounts these routers, the handlers cannot be reached by a running service.
