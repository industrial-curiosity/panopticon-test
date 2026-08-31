---
type: component
---

# clients

## Responsibility

The `clients` component provides synchronous HTTP clients for the orders API, order-processing
service, and warehouse ERP. Each helper creates an `httpx.Client`, calls a fixed relative path,
raises for unsuccessful HTTP status codes, and returns decoded response data.

## Interfaces

The component consumes `orders-api`, `order-processing-api`, and `warehouse-erp`. See
[interfaces.md](../interfaces.md) for the canonical names and source files.

## Key modules

- `inventory/clients/orders.py` — gets one order or lists orders from `orders-api`.
- `inventory/clients/order_processing.py` — gets processing status from
  `order-processing-api`.
- `inventory/clients/erp.py` — reads warehouse stock and requests replenishment from
  `warehouse-erp`.

## Configuration

The following environment variables are required when their modules are imported:

- `ORDERS_API_URL` — base URL for `orders-api`.
- `ORDER_PROCESSING_URL` — base URL for `order-processing-api`.
- `WAREHOUSE_ERP_URL` — base URL for `warehouse-erp`.

No client timeout, retry, authentication, or feature-flag configuration is declared in these
modules.

## Failure modes

Missing environment variables fail during module import. HTTP transport failures and unsuccessful
responses propagate from `httpx`; the code does not add retries or local fallback behavior. No
logging or metrics are emitted by these clients.
