# Complex-organization instance template

The complex-organization template creates a reviewable, non-secret overlay for
a private Panopticon instance. It extends the existing trusted provider
contract; it does not create a provider runtime or permit profile-controlled
workflow injection.

## Minimal workflow

Run these commands from the public template checkout. `PROFILE` is one of the
concrete synthetic examples or a private profile that follows the same schema.
`INSTANCE` is the private instance checkout and `OVERLAY` is a new review
directory.

```bash
python3 -m panopticon.organization_template validate PROFILE
python3 -m panopticon.organization_template generate PROFILE --instance-root INSTANCE --output OVERLAY
python3 -m panopticon.organization_template apply OVERLAY --instance-root INSTANCE --check
python3 -m panopticon.organization_template apply OVERLAY --instance-root INSTANCE
```

Review `OVERLAY/overlay-manifest.json` and every file under `OVERLAY/files/`
before the final command. Commit the applied instance changes through the
normal reviewed instance workflow. The `--check` operation is read-only.

For a public synthetic fixture, add `--public` to `validate` and `generate`:

```bash
python3 -m panopticon.organization_template validate templates/complex-organization/direct-oidc.json --public
python3 -m panopticon.organization_template generate templates/complex-organization/direct-oidc.json --instance-root INSTANCE --output OVERLAY --public
```

## Profile contract

Profiles are versioned JSON documents. The machine-readable schema is
[`templates/complex-organization/profile.schema.json`](../templates/complex-organization/profile.schema.json).
The generator additionally applies the trusted provider registry and secret
safety rules.

Required fields are:

- `schema_version`: currently `1`.
- `provider`: `litellm`, `openai`, or `bedrock`.
- `identity`: organization-owned identity references. Bedrock
  `github-oidc` requires `role_reference`; every profile requires a
  `child_provisioning_reference`.
- `child_identity`: non-secret per-child provisioning instructions and a
  diagnostic URL.

The optional `credential_mode` is only valid for Bedrock. `github-oidc` is the
default; `instance-managed` requires the bounded `broker` object:

```json
{
  "credential_mode": "instance-managed",
  "broker": {
    "action": "example-org/panopticon-broker/.github/actions/aws-credentials@v1.2.3",
    "region_output": "aws_region"
  }
}
```

The action reference accepts a branch, tag, or full 40-character commit SHA.
It is rendered only inside the fixed
`.github/actions/panopticon-aws-credentials/action.yml` wrapper. Profiles cannot
choose a reusable workflow, replace that wrapper path, provide child steps, or
provide action inputs.

`names.secrets` and `names.variables` may override logical Actions names known
to the selected provider. Unknown logical names, endpoint overrides for OpenAI,
Bedrock OIDC names in instance-managed mode, and reserved `GITHUB_` names are
rejected. Provider paths, permissions, mappings, defaults, and compatibility
revisions are derived from the registry and caller renderer.

Optional request-budget values use two explicit maps:

- `defaults` contains non-secret values only when the source is
  `instance-config`.
- `default_sources` names one of `organization-variable`, `instance-action`,
  `instance-config`, or `workflow-default`.

The validator rejects a promised source that cannot provide that logical value,
an instance-config promise without a value, and `job_timeout_minutes` as an
instance default. GitHub resolves job timeout before an Action runs.

Advanced optional sections are `workflow_access`, `internal_registries`,
`gating`, `workflow_ref`, and `protected_paths`. Every protected-path entry
requires a reason, owner, upstream replacement reference, last reconciliation
result, and removal condition. The fixed generated architecture path and the
provider-derived instance-managed wrapper are protection metadata, not
organization debt; attempting to list either derived path in `protected_paths`
is rejected during profile validation.

## Generated output

The overlay contains:

- `panopticon.config.json`, containing only accepted instance configuration
  fields. It never contains computed provider or caller revisions.
- The fixed credential wrapper when Bedrock `instance-managed` is selected.
- An instance-wide checklist for reusable-workflow access and provider
  configuration.
- A separate child checklist covering all four gates: reusable-workflow access,
  effective provider configuration, caller identity and credentials, and real
  provider-request compatibility.
- A protected-path debt register.
- `overlay-manifest.json`, containing destination content digests, destination
  preimage digests or absence, protection classes/reasons, and computed
  provider/caller revisions.

Protection classes are `template-generated`, `provider-derived`, and
`organization-declared`. Sync and tooling-currency reports keep those classes
separate. Only organization-declared paths require debt metadata.

## Security and failure behavior

Profiles contain names, references, and non-secret setup choices. Credential
values, private-key blocks, token prefixes, likely secret assignments, unresolved
placeholders, and private organization identifiers in public fixtures are
rejected. Error messages identify field paths and rules without echoing values.

Generation validates the full profile and renders all files in memory before
publishing to an absent or empty output directory. A rendering or safety
failure leaves no partial overlay. Generation is deterministic for the same
profile and instance preimages.

Apply validates the manifest and every destination preimage before writing. A
stale destination, non-file collision, undeclared overlay file, or manifest
digest mismatch stops the operation before any instance file changes. Apply
writes only declared files, never replaces the instance directory, and never
deletes unrelated content.

## Child onboarding and rollback

After the reviewed overlay is applied and committed, initialize a child through
the public launcher and review its generated caller:

```bash
curl -fsSL https://raw.githubusercontent.com/industrial-curiosity/panopticon-ay-eye/main/install.py | PANOPTICON_INSTANCE='ORG/INSTANCE' python3
python3 -m panopticon.init_repo --instance ORG/INSTANCE
```

The child checklist is the recovery source for per-child identity provisioning.
A reusable workflow does not transfer the caller repository's OIDC subject.
Keep organization role registrations, account identifiers, and credential
values in the organization's private setup system.

To roll back before commit, discard the overlay. After an instance commit,
restore the previous reviewed `panopticon.config.json`, wrapper, and generated
guidance through the normal instance change process; do not delete unrelated
instance files manually.

The profiles shipped with the public template are concrete, reserved examples:
[`direct-oidc.json`](../templates/complex-organization/direct-oidc.json) and
[`instance-managed.json`](../templates/complex-organization/instance-managed.json).
They are validated with the same path as private profiles and contain no real
organization identifiers or credential values.
