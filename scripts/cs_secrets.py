#!/usr/bin/env python3
"""Resolve secrets for skill runs without ever committing or printing them.

Resolution order for a named secret:

  1. An environment variable with that name (e.g. PATREON_ACCESS_TOKEN).
  2. 1Password, when OP_SERVICE_ACCOUNT_TOKEN is set: the secret reference
     (op://<vault>/<item>/<field>) is resolved with the 1Password SDK, or
     with the `op` CLI if the SDK is not installed.
  3. A git-ignored JSON file under .claude/data/, when one is registered
     for that secret.

Every platform that runs the skills (Claude Routines, an OpenAI environment,
GitHub Actions) holds only the 1Password service-account token; the secret
itself lives in one vault. Importable and runnable:

  python3 scripts/cs_secrets.py check patreon    # exit 0 if resolvable, prints the source only
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REGISTRY = {
    "patreon": {
        "env": "PATREON_ACCESS_TOKEN",
        "op_ref": "op://API Tokens/Patreon creator token/credential",
        "file": ".claude/data/patreon-config.json",
        "file_key": "creator_access_token",
    },
}


def repo_root() -> Path:
    try:
        return Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                                   text=True, check=True).stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path(__file__).resolve().parents[1]


def _op_cli() -> str | None:
    """Path to the op CLI: on PATH, or where bootstrap_run.sh installs it."""
    found = shutil.which("op")
    if found:
        return found
    local = Path.home() / ".local" / "bin" / "op"
    return str(local) if local.is_file() and os.access(local, os.X_OK) else None


def _from_onepassword(ref: str) -> str | None:
    token = os.environ.get("OP_SERVICE_ACCOUNT_TOKEN")
    if not token:
        return None
    # The op CLI first: it honors SSL_CERT_FILE and HTTPS_PROXY, which the
    # sandboxed Routine environment needs; the SDK ships its own roots.
    cli = _op_cli()
    if cli:
        proc = subprocess.run([cli, "read", ref], capture_output=True, text=True,
                              env={**os.environ, "OP_SERVICE_ACCOUNT_TOKEN": token})
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
        print(f"secrets: op read failed: {proc.stderr.strip()[:300]}", file=sys.stderr)
    try:  # 1Password SDK (pip install onepassword-sdk)
        import asyncio
        from onepassword import Client  # type: ignore

        async def _resolve() -> str:
            client = await Client.authenticate(auth=token, integration_name="Clean Streets skills",
                                               integration_version="v1.0.0")
            return await client.secrets.resolve(ref)

        return asyncio.run(_resolve())
    except ImportError:
        pass
    except Exception as exc:  # auth or lookup failure: fall through to the CLI
        # The message names the cause (bad token, unknown vault/item, TLS,
        # network); it never contains the secret. Redact anything token-like.
        msg = re.sub(r"ops_[A-Za-z0-9_-]+", "[token]", str(exc))[:300]
        print(f"secrets: 1Password SDK failed: {msg}", file=sys.stderr)
    return None


def resolve(name: str, with_source: bool = False):
    """Return the secret value (or (value, source) with with_source). None if unavailable."""
    spec = REGISTRY[name]
    value = os.environ.get(spec["env"])
    if value:
        return (value, "env") if with_source else value
    value = _from_onepassword(spec["op_ref"])
    if value:
        return (value, "1password") if with_source else value
    path = repo_root() / spec["file"]
    if path.exists():
        try:
            value = json.loads(path.read_text(encoding="utf-8")).get(spec["file_key"])
        except (ValueError, OSError):
            value = None
        if value:
            return (value, "file") if with_source else value
    return (None, None) if with_source else None


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 2 or args[0] != "check" or args[1] not in REGISTRY:
        print(f"usage: cs_secrets.py check <{'|'.join(REGISTRY)}>", file=sys.stderr)
        return 2
    _, source = resolve(args[1], with_source=True)
    if source:
        print(f"OK: {args[1]} secret available from {source}")
        return 0
    spec = REGISTRY[args[1]]
    op_state = ("OP_SERVICE_ACCOUNT_TOKEN present but the 1Password lookup failed (see lines above)"
                if os.environ.get("OP_SERVICE_ACCOUNT_TOKEN") else "no OP_SERVICE_ACCOUNT_TOKEN")
    print(f"WARN: {args[1]} secret not available: no {spec['env']}; {op_state}; no {spec['file']}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
