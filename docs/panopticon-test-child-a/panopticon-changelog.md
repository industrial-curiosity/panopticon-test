# Panopticon changelog

Entries record when Panopticon's doc-generation found and resolved drift between committed
documentation and the repo's actual current state. Generated file — keep, edit, or discard at
your own commit step.

## 2026-08-09

- **`docs/operations.md`, `docs/architecture.md`** — the managed `## Panopticon analysis scope`
  section (with its `panopticon-analysis-scope` markers) and the analysis-scope link directly
  below the architecture diagram are now required by the doc tooling (`panopticon/docs.py`
  validates both); both files predated that change. Ran
  `python3 -m panopticon.docs render` to insert the managed scope section, moved it to the top of
  `operations.md` to match the operations template's heading order, and added the
  `[Panopticon analysis scope](operations.md#panopticon-analysis-scope)` link below the diagram in
  `architecture.md`. No interface, component, or code drift was found.

## 2026-07-26

- **`inventory/clients/order_processing.py`, `panopticon/index.json`, and generated docs** — the
  explicit interface hint and index used `order-processing-queue` even though the source only
  performs HTTP status lookups. Renamed the canonical interface to
  `order-processing-status` and regenerated `docs/interfaces.md`.
- **`README.md`, `docs/architecture.md`, component docs, and `py-inventory-service.md`** —
  documentation asserted ownership, external systems, and an ownership dispute that are not
  established by the local source or local index. Replaced those claims with source-backed roles
  and the local index's `null` owner state; refreshed the required architecture links.

## 2026-07-12

- **`docs/architecture.md`** — the `## Architecture diagram` section required by the current
  `architecture-template.md` was missing entirely (template was updated to require it; the
  previously generated file predated that change). Added the section: a Mermaid diagram of the
  six components (`api`, `clients`, `events`, `queue`, `storage`, `db`) and their interface
  edges, grounded in `panopticon/index.json` and the current source (no cross-component imports,
  per the existing "Data flow" section), plus the required back-link to the org diagram.
- **`README.md`** — repository structure, interfaces table, and environment variables table
  predated `inventory/api/orders_routes.py` and `inventory/clients/order_processing.py`. Updated
  to list both files, added the `orders-api` ownership-dispute note (owned here via
  `orders_routes.py` while also consumed from the order service's existing API via
  `clients/orders.py`), added the `order-processing-queue` interface row, and added the
  `ORDER_PROCESSING_URL` environment variable row — matching what `docs/architecture.md` and
  `docs/operations.md` already documented.
- **`docs/architecture.md`** — the org-diagram back-link used an absolute GitHub URL
  (`https://github.com/.../docs/architecture.md#...`) instead of the relative markdown link the
  current `architecture-template.md` requires. Replaced with
  `[org diagram](../architecture.md#panopticon-test-child-a)`.
- **`docs/architecture.md`**, **`docs/components/clients.md`** — both asserted that another org
  repo declares an `sqs` interface under the `order-processing-queue` canonical name. Nothing in
  this repo's index or source evidences another repo's declaration (local repo indexes never
  contain cross-repo conflict entries — those exist only in the instance's compiled index).
  Replaced the unverifiable claim with a plain statement that no owner is recorded locally and
  this repo has no visibility into other repos' declarations.
- **`py-inventory-service.md`** — described an `infra/`-based extraction design (deterministic
  REST/OpenAPI and Kafka parsers over `infra/*.yaml`/`.properties` files) that doesn't exist in
  this repo: there is no `infra/` directory, and `panopticon/index.json` shows every interface
  (including `inventory-api`, which the fixture said the OpenAPI parser would catch
  deterministically) extracted via LLM fallback directly from `.py` source. The fixture also
  omitted `inventory/api/orders_routes.py` and the `order-processing-queue` interface entirely,
  and described a "clean compiled index... no ownership disputes" though this repo's own index
  already shows `orders-api` both produced and consumed locally. Rewrote the fixture to describe
  the repo as it actually stands today (confirmed with the user before rewriting, given the scale
  of the divergence).
