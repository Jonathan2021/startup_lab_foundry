"""Verify an installed wheel from an empty cwd using only disposable local data.

The caller supplies a fresh virtual environment with locked runtime dependencies
and the wheel installed. No Foundry imports, development dependencies, operator
database, parent checkout, or network provider are needed by this harness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import sqlite3
import subprocess
import time
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen


def verify(python: Path, output: Path) -> dict[str, Any]:
    """Migrate/seed, back up, restore and restart the packaged CLI/HTTP app."""
    # Keep the venv's executable path: resolving its symlink loses venv identity.
    python = python.absolute()
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    cwd = output / "empty-cwd"
    cwd.mkdir()
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("FOUNDRY_") and key not in {"PYTHONPATH", "PYTHONHOME"}
    }
    env.update(
        XDG_DATA_HOME=str(output / "xdg"),
        FOUNDRY_REQUESTS_DIR=str(output / "requests"),
    )

    def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [str(python), "-I", *args],
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            timeout=60,
        )
        if check and result.returncode:
            raise RuntimeError(f"Installed command failed: {result.stderr[-4000:]}")
        return result

    def cli(store: Path, *args: str, check: bool = True) -> Any:
        result = run("-m", "startup_foundry", "--store", str(store), *args, check=check)
        return json.loads(result.stdout) if check else result

    package = json.loads(
        run(
            "-c",
            "import json,startup_foundry; print(json.dumps({"
            "'path':startup_foundry.__file__,'version':startup_foundry.__version__}))",
        ).stdout
    )
    if python.parent.parent not in Path(package["path"]).parents:
        raise RuntimeError("Verification must import the installed wheel from its venv")
    store = output / "demo.local.db"
    manifest = json.loads(
        run("-m", "startup_foundry.demo", "--store", str(store)).stdout
    )
    original = cli(store, "venture", "list")
    for entry in manifest["ventures"]:
        state = cli(
            store,
            "agent",
            "resume",
            "--venture-id",
            entry["venture_id"],
            "--format",
            "json",
        )
        if state["workspace_id"] != entry["workspace_id"]:
            raise RuntimeError("Installed lifecycle data did not survive CLI restart")
    backup = output / "backup.local.db"
    if not cli(store, "storage", "backup", "--output", str(backup))["verified"]:
        raise RuntimeError("Backup did not verify")
    backup_hash = hashlib.sha256(backup.read_bytes()).hexdigest()
    refused = cli(store, "storage", "backup", "--output", str(backup), check=False)
    if (
        not refused.returncode
        or hashlib.sha256(backup.read_bytes()).hexdigest() != backup_hash
    ):
        raise RuntimeError("Existing backup must be preserved and overwrite refused")
    restored = output / "restored.local.db"
    shutil.copy2(backup, restored)
    if cli(restored, "venture", "list") != original:
        raise RuntimeError("Restored venture records differ from the source")
    with sqlite3.connect(restored) as db:
        if db.execute("PRAGMA integrity_check").fetchone() != ("ok",):
            raise RuntimeError("Restored database failed integrity check")

    # Exercise wheel templates/static files twice, across a full process restart.
    for attempt in range(2):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        with (output / f"http-{attempt}.log").open("w") as log:
            process = subprocess.Popen(
                [
                    str(python),
                    "-I",
                    "-m",
                    "startup_foundry",
                    "--store",
                    str(restored),
                    "ui",
                    "--port",
                    str(port),
                ],
                cwd=cwd,
                env=env,
                stdout=log,
                stderr=log,
            )
            try:
                base = f"http://127.0.0.1:{port}"
                deadline = time.monotonic() + 20
                while True:
                    if process.poll() is not None:
                        raise RuntimeError(
                            f"Installed server exited; see http-{attempt}.log"
                        )
                    try:
                        with urlopen(base + "/", timeout=2) as response:
                            if response.status != 200:
                                raise RuntimeError("Installed home page unavailable")
                        break
                    except URLError:
                        if time.monotonic() > deadline:
                            raise RuntimeError(
                                "Installed server readiness timeout"
                            ) from None
                        time.sleep(0.1)
                for path in [
                    "/help",
                    "/static/console.css",
                    "/static/console.js",
                    "/static/decisions.css",
                    "/static/decisions.js",
                    "/ventures/" + manifest["ventures"][0]["venture_id"],
                ]:
                    with urlopen(base + path, timeout=5) as response:
                        if response.status != 200 or not response.read():
                            raise RuntimeError("Missing packaged HTTP asset: " + path)
            finally:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
    if (
        list(cwd.iterdir())
        or (output / "xdg/startup-foundry/foundry.local.db").exists()
    ):
        raise RuntimeError(
            "Explicit test store must not create a default or cwd database"
        )
    report = {
        "status": "pass",
        "version": package["version"],
        "synthetic_ventures": len(manifest["ventures"]),
        "checks": [
            "installed-wheel",
            "migrations",
            "lifecycle-resume",
            "backup",
            "overwrite-refusal",
            "restore-integrity",
            "http-assets",
            "restart",
            "explicit-store-isolation",
        ],
    }
    (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.python, args.output_dir), indent=2))


if __name__ == "__main__":
    main()
