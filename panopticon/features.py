"""Trusted feature registry, selection, receipts, and lifecycle helpers.

Feature configuration names only a template-owned feature ID and mode. The
registry owns source paths and child destinations, so instance configuration
cannot select arbitrary code or files. This module is intentionally
stdlib-only because it is vendored into initialized child repositories.
"""

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
from pathlib import Path, PurePosixPath


FEATURE_MODES = ("disabled", "advisory", "blocking")
FEATURE_MANIFEST_VERSION = 1
FEATURE_RECEIPT_VERSION = 1
FEATURES_ROOT = Path("features")
FEATURE_MANIFEST_PATH = FEATURES_ROOT / "manifest.json"
FEATURE_RECEIPT_PATH = Path("panopticon") / "feature-receipt.json"
FEATURE_SOURCE_PREFIX = "features/"
FEATURE_ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")


class FeatureConfigError(ValueError):
    """A feature registry, configuration, or receipt is invalid."""


def _canonical_json(document):
    return json.dumps(document, sort_keys=True, separators=(",", ":")).encode("utf-8")


def manifest_revision(manifest):
    """Return the stable revision for a validated registry document."""
    return hashlib.sha256(_canonical_json(manifest)).hexdigest()


def _safe_relative_path(value, description):
    if not isinstance(value, str) or not value or "\\" in value:
        raise FeatureConfigError(f"{description} must be a non-empty POSIX relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise FeatureConfigError(f"{description} must stay within its managed namespace: {value!r}")
    return value


def _feature_destination_allowed(feature_id, destination):
    return (
        destination.startswith(f".agents/skills/panopticon-feature-{feature_id}/")
        or destination == f"panopticon/feature_{feature_id}.py"
    )


def validate_manifest(document, root="."):
    """Validate and return a template-owned feature registry."""
    if not isinstance(document, dict):
        raise FeatureConfigError("features manifest must be a JSON object")
    if set(document) != {"schema_version", "features"}:
        raise FeatureConfigError(
            "features manifest must contain exactly schema_version and features"
        )
    if document["schema_version"] != FEATURE_MANIFEST_VERSION:
        raise FeatureConfigError(
            f"features manifest has unsupported schema_version {document['schema_version']!r}; "
            f"expected {FEATURE_MANIFEST_VERSION}"
        )
    features = document["features"]
    if not isinstance(features, dict) or not features:
        raise FeatureConfigError("features manifest 'features' must be a non-empty object")

    destinations = set()
    core_paths = set()
    local_manifest = Path(root) / "panopticon" / "local-tooling.json"
    if local_manifest.is_file():
        try:
            tooling = json.loads(local_manifest.read_text(encoding="utf-8"))
            core_paths = {f"panopticon/{name}" for name in tooling.get("modules", [])}
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            # The local-tooling manifest is validated by its own boundary. Do not hide a
            # feature-registry error behind a secondary diagnostic while loading it here.
            core_paths = set()
    for feature_id, definition in features.items():
        if not isinstance(feature_id, str) or not FEATURE_ID_RE.fullmatch(feature_id):
            raise FeatureConfigError(f"features manifest has invalid feature ID {feature_id!r}")
        if not isinstance(definition, dict) or set(definition) != {"modes", "artifacts"}:
            raise FeatureConfigError(
                f"feature {feature_id!r} must contain exactly modes and artifacts"
            )
        modes = definition["modes"]
        if not isinstance(modes, list) or modes != list(FEATURE_MODES):
            raise FeatureConfigError(
                f"feature {feature_id!r} modes must be {list(FEATURE_MODES)}"
            )
        artifacts = definition["artifacts"]
        if not isinstance(artifacts, list) or not artifacts:
            raise FeatureConfigError(f"feature {feature_id!r} artifacts must be a non-empty array")
        for artifact in artifacts:
            if not isinstance(artifact, dict) or set(artifact) != {"source", "destination"}:
                raise FeatureConfigError(
                    f"feature {feature_id!r} artifacts must contain source and destination"
                )
            source = _safe_relative_path(artifact["source"], f"feature {feature_id!r} source")
            destination = _safe_relative_path(
                artifact["destination"], f"feature {feature_id!r} destination"
            )
            if not source.startswith(f"{feature_id}/"):
                raise FeatureConfigError(
                    f"feature {feature_id!r} source must stay under its package: {source!r}"
                )
            if not _feature_destination_allowed(feature_id, destination):
                raise FeatureConfigError(
                    f"feature {feature_id!r} destination is outside its approved namespace: "
                    f"{destination!r}"
                )
            if destination in destinations:
                raise FeatureConfigError(f"duplicate feature destination: {destination}")
            if destination in core_paths:
                raise FeatureConfigError(
                    f"feature destination collides with core managed resource: {destination}"
                )
            destinations.add(destination)
    return document


def load_manifest(root="."):
    path = Path(root) / FEATURE_MANIFEST_PATH
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FeatureConfigError(f"features manifest is missing: {path}") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FeatureConfigError(f"invalid features manifest at {path}: {exc}") from exc
    return validate_manifest(document, root)


def load_manifest_bytes(source, root="."):
    try:
        document = json.loads(source)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FeatureConfigError(f"invalid features manifest JSON: {exc}") from exc
    return validate_manifest(document, root)


def validate_feature_config(features, manifest):
    """Return effective modes, defaulting every registered feature to disabled."""
    if features is None:
        features = {}
    if not isinstance(features, dict):
        raise FeatureConfigError("org config 'features' must be an object")
    unknown = sorted(set(features) - set(manifest["features"]))
    if unknown:
        raise FeatureConfigError(f"org config has unregistered feature IDs: {unknown}")
    effective = {feature_id: "disabled" for feature_id in manifest["features"]}
    for feature_id, entry in features.items():
        if not isinstance(entry, dict) or set(entry) != {"mode"}:
            raise FeatureConfigError(
                f"org config feature {feature_id!r} must contain exactly the mode field"
            )
        mode = entry["mode"]
        if mode not in FEATURE_MODES:
            raise FeatureConfigError(
                f"feature {feature_id!r} mode must be one of {list(FEATURE_MODES)}, got {mode!r}"
            )
        effective[feature_id] = mode
    return effective


def selected_artifacts(manifest, modes):
    """Return registry artifact descriptors selected by enabled feature modes."""
    selected = []
    for feature_id, mode in modes.items():
        if mode == "disabled":
            continue
        for artifact in manifest["features"][feature_id]["artifacts"]:
            selected.append({
                "feature": feature_id,
                "source": artifact["source"],
                "destination": artifact["destination"],
            })
    return selected


def _receipt_entries(entries, description):
    if not isinstance(entries, list):
        raise FeatureConfigError(f"feature receipt {description} must be an array")
    normalized = []
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"feature", "destination"}:
            raise FeatureConfigError(
                f"feature receipt {description} entries must contain feature and destination"
            )
        feature_id = entry["feature"]
        destination = _safe_relative_path(entry["destination"], "feature receipt destination")
        key = (feature_id, destination)
        if key in seen:
            raise FeatureConfigError(f"feature receipt contains duplicate entry: {key}")
        seen.add(key)
        normalized.append({"feature": feature_id, "destination": destination})
    return normalized


def validate_receipt(document, manifest):
    """Validate a receipt before any receipt-owned path can be removed."""
    if not isinstance(document, dict) or set(document) != {
        "schema_version", "registry_revision", "features", "artifacts", "pending_removals"
    }:
        raise FeatureConfigError(
            "feature receipt must contain exactly schema_version, registry_revision, "
            "features, artifacts, and pending_removals"
        )
    if document["schema_version"] != FEATURE_RECEIPT_VERSION:
        raise FeatureConfigError(
            f"feature receipt has unsupported schema_version {document['schema_version']!r}"
        )
    if not isinstance(document["registry_revision"], str) or not document["registry_revision"]:
        raise FeatureConfigError("feature receipt registry_revision must be a non-empty string")
    modes = validate_feature_config(document["features"], manifest)
    installed = _receipt_entries(document["artifacts"], "artifacts")
    pending = _receipt_entries(document["pending_removals"], "pending_removals")
    allowed = {
        (feature_id, artifact["destination"])
        for feature_id, definition in manifest["features"].items()
        for artifact in definition["artifacts"]
    }
    for entry in [*installed, *pending]:
        if (entry["feature"], entry["destination"]) not in allowed:
            raise FeatureConfigError(
                f"feature receipt entry is not registered: {entry['feature']} / "
                f"{entry['destination']}"
            )
    installed_keys = {(entry["feature"], entry["destination"]) for entry in installed}
    if not set((entry["feature"], entry["destination"]) for entry in pending) <= installed_keys:
        raise FeatureConfigError("feature receipt pending_removals must be installed artifacts")
    return {"modes": modes, "artifacts": installed, "pending_removals": pending}


def load_receipt(child_root=".", manifest=None):
    path = Path(child_root) / FEATURE_RECEIPT_PATH
    if not path.is_file():
        return None
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FeatureConfigError(f"invalid feature receipt at {path}: {exc}") from exc
    if manifest is not None:
        return validate_receipt(document, manifest)
    try:
        return validate_receipt(document, load_manifest(child_root))
    except FeatureConfigError as exc:
        if "features manifest is missing" not in str(exc):
            raise
        if not isinstance(document, dict) or set(document) != {
            "schema_version", "registry_revision", "features", "artifacts", "pending_removals"
        }:
            raise FeatureConfigError(
                f"feature receipt at {path} cannot be validated without its registry: invalid shape"
            ) from exc
        if document["schema_version"] != FEATURE_RECEIPT_VERSION:
            raise FeatureConfigError(
                f"feature receipt at {path} has unsupported schema_version"
            ) from exc
        if not isinstance(document["registry_revision"], str) or not document["registry_revision"]:
            raise FeatureConfigError(f"feature receipt at {path} has no registry revision") from exc
        for feature_id, entry in document["features"].items():
            if not FEATURE_ID_RE.fullmatch(feature_id) or not isinstance(entry, dict):
                raise FeatureConfigError(f"feature receipt at {path} has invalid feature state") from exc
            if set(entry) != {"mode"} or entry["mode"] not in FEATURE_MODES:
                raise FeatureConfigError(f"feature receipt at {path} has invalid feature mode") from exc
        installed = _receipt_entries(document["artifacts"], "artifacts")
        pending = _receipt_entries(document["pending_removals"], "pending_removals")
        for entry in [*installed, *pending]:
            if not FEATURE_ID_RE.fullmatch(entry["feature"]):
                raise FeatureConfigError(f"feature receipt at {path} has invalid feature ID") from exc
            if not _feature_destination_allowed(entry["feature"], entry["destination"]):
                raise FeatureConfigError(
                    f"feature receipt at {path} has an unapproved destination "
                    f"{entry['destination']!r}"
                ) from exc
        installed_keys = {(entry["feature"], entry["destination"]) for entry in installed}
        if not set((entry["feature"], entry["destination"]) for entry in pending) <= installed_keys:
            raise FeatureConfigError(f"feature receipt at {path} has pending entries not installed") from exc
        return {
            "modes": {feature_id: entry["mode"] for feature_id, entry in document["features"].items()},
            "artifacts": installed,
            "pending_removals": pending,
        }


def build_receipt(manifest, modes, installed, pending_removals=()):
    mode_values = (
        {feature_id: {"mode": mode} for feature_id, mode in modes.items()}
        if all(isinstance(mode, str) for mode in modes.values())
        else modes
    )
    effective_modes = validate_feature_config(mode_values, manifest)
    def unique(entries):
        result = []
        seen = set()
        for entry in entries:
            key = (entry["feature"], entry["destination"])
            if key not in seen:
                result.append({"feature": entry["feature"], "destination": entry["destination"]})
                seen.add(key)
        return result

    installed = unique(installed)
    pending_removals = unique(pending_removals)
    return {
        "schema_version": FEATURE_RECEIPT_VERSION,
        "registry_revision": manifest_revision(manifest),
        "features": {
            feature_id: {"mode": mode} for feature_id, mode in effective_modes.items()
        },
        "artifacts": [
            entry for entry in installed
        ],
        "pending_removals": [
            entry for entry in pending_removals
        ],
    }


def retired_artifacts(previous, desired):
    desired_keys = {(entry["feature"], entry["destination"]) for entry in desired}
    return [
        entry for entry in previous["artifacts"]
        if (entry["feature"], entry["destination"]) not in desired_keys
    ]


def stage_artifacts(manifest, modes, fetch):
    """Fetch every selected feature byte before returning anything to be written."""
    staged = []
    for entry in selected_artifacts(manifest, modes):
        source_path = f"{FEATURE_SOURCE_PREFIX}{entry['source']}"
        content = fetch(source_path)
        if not isinstance(content, bytes):
            raise FeatureConfigError(f"feature source {source_path} did not return bytes")
        staged.append({**entry, "content": content})
    return staged


def write_staged_artifacts(staged, child_root="."):
    for entry in staged:
        path = Path(child_root) / entry["destination"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(entry["content"])


def write_receipt(receipt, child_root="."):
    path = Path(child_root) / FEATURE_RECEIPT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as handle:
            json.dump(receipt, handle, indent=2, sort_keys=True)
            handle.write("\n")
            temp_path = handle.name
        os.replace(temp_path, path)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
    return path


def cleanup_retired(retired, child_root=".", interactive=False, prompt=input, print_fn=print):
    """Delete only validated receipt entries and return (deleted, pending)."""
    for entry in retired:
        if (
            not isinstance(entry, dict)
            or set(entry) != {"feature", "destination"}
            or not isinstance(entry["feature"], str)
            or not FEATURE_ID_RE.fullmatch(entry["feature"])
            or not _feature_destination_allowed(
                entry["feature"], _safe_relative_path(entry["destination"], "retired feature destination")
            )
        ):
            raise FeatureConfigError("retired feature entry is outside a registered managed namespace")
    if not retired:
        return [], []
    print_fn("The instance maintainer disabled these feature artifacts:")
    for entry in retired:
        print_fn(f"  - {entry['feature']}: {entry['destination']}")
    if interactive:
        answer = prompt("Delete these files? [Y/n] ")
        if answer.strip().lower() not in {"", "y", "yes"}:
            print_fn("Cleanup declined; feature artifacts remain pending.")
            return [], list(retired)
    deleted = []
    for entry in retired:
        path = Path(child_root) / entry["destination"]
        if path.is_file():
            path.unlink()
            print_fn(f"  deleted {entry['destination']}")
        deleted.append(entry)
    return deleted, []


def _load_feature_helper(feature_id, root):
    candidates = [
        Path(root) / "panopticon" / f"feature_{feature_id}.py",
        Path(root) / FEATURES_ROOT / feature_id / "okf.py",
    ]
    path = next((candidate for candidate in candidates if candidate.is_file()), None)
    if path is None:
        raise FeatureConfigError(
            f"feature {feature_id!r} is enabled but its helper is missing; rerun bootstrap or sync"
        )
    module_name = f"panopticon_feature_{feature_id.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise FeatureConfigError(f"could not load feature helper {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_enabled_features(modes, root=".", docs_root="docs", print_fn=print):
    """Run enabled feature validators and return (findings, blocking_failure)."""
    findings = []
    blocking_failure = False
    for feature_id, mode in modes.items():
        if mode == "disabled":
            continue
        helper = _load_feature_helper(feature_id, root)
        validator = getattr(helper, "validate_bundle", None)
        if not callable(validator):
            raise FeatureConfigError(f"feature {feature_id!r} helper has no validate_bundle function")
        feature_findings = list(validator(docs_root))
        for finding in feature_findings:
            message = f"{feature_id} ({mode}): {finding}"
            findings.append(message)
            print_fn(message)
        blocking_failure = blocking_failure or bool(feature_findings) and mode == "blocking"
    return findings, blocking_failure


def load_effective_modes(root="."):
    """Load effective modes from a local instance checkout."""
    from .config import load_org_config

    manifest = load_manifest(root)
    return manifest, validate_feature_config(load_org_config(root).get("features"), manifest)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Resolve and validate Panopticon feature state.")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="run enabled deterministic feature checks")
    check.add_argument("--root", default=".")
    check.add_argument("--docs-root", default="docs")
    args = parser.parse_args(argv)
    if args.command == "check":
        try:
            _, modes = load_effective_modes(args.root)
            _, blocking = validate_enabled_features(modes, args.root, args.docs_root)
        except FeatureConfigError as exc:
            print(f"feature check could not run: {exc}")
            return 1
        return 2 if blocking else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
