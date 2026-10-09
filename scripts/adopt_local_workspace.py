"""One-time, non-overwriting adoption of the documented local campaign stores.

This is an explicit migration aid for the 2026-10-02 workspace, not a general
untrusted-database merger. Both source files remain unchanged.
"""

import hashlib
import json
import sqlite3
from pathlib import Path

from startup_foundry.config import load_settings
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.storage import backup_sqlite, sqlite_path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/inquiry/local-console-2026-10-02"
CAMPAIGN = ROOT / ".local/portfolio-campaign/campaign.local.db"
EARLIER = ROOT / ".local/portfolio-realignment.local.db"
STAGING = ROOT / ".local/console-adoption/staging.local.db"
TARGET = sqlite_path(load_settings().database_url)
if TARGET.exists():
    raise SystemExit("Working store already exists; adoption must not overwrite it.")
if STAGING.exists():
    raise SystemExit(
        "Staging store exists; inspect it before choosing a fresh attempt."
    )
source_hashes = {
    str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in [CAMPAIGN, EARLIER]
}
backup_sqlite("sqlite:///" + str(CAMPAIGN), STAGING)
merged = {}
with sqlite3.connect(EARLIER.as_uri() + "?mode=ro", uri=True) as source:
    source.row_factory = sqlite3.Row
    with sqlite3.connect(STAGING) as target:
        target.row_factory = sqlite3.Row
        target.execute("PRAGMA foreign_keys=ON")
        target.execute("BEGIN")
        target.execute("PRAGMA defer_foreign_keys=ON")
        tables = [
            r[0]
            for r in source.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name"
                " NOT IN ('alembic_version','sqlite_sequence')"
            )
        ]
        for table in tables:
            # Identifiers come only from the known local schema, not attachments.
            if not table.replace("_", "").isalnum():
                raise RuntimeError("Unexpected schema identifier")
            count = 0
            for row in source.execute(f'SELECT * FROM "{table}"'):
                existing = target.execute(
                    f'SELECT * FROM "{table}" WHERE id=?', (row["id"],)
                ).fetchone()
                if existing:
                    if (
                        table == "portfolios"
                        and row["id"] == "portfolio-default"
                        and row["key"] == existing["key"] == "default"
                    ):
                        continue  # one intentional shared default-portfolio identity
                    if dict(existing) != dict(row):
                        raise RuntimeError(
                            f"Conflicting retained identity: {table}/{row['id']}"
                        )
                    continue
                columns = ",".join('"' + key + '"' for key in row.keys())
                placeholders = ",".join("?" for _ in row)
                target.execute(
                    f'INSERT INTO "{table}" ({columns}) VALUES ({placeholders})',
                    tuple(row),
                )
                count += 1
            if count:
                merged[table] = count
        assert not target.execute("PRAGMA foreign_key_check").fetchall()
upgrade_database("sqlite:///" + str(STAGING))
engine = create_db_engine("sqlite:///" + str(STAGING))
try:
    result = PortfolioService(create_session_factory(engine)).import_campaign(
        Path("/home/jonathan/Downloads"),
        ROOT / "docs/inquiry/portfolio-campaign",
    )
finally:
    engine.dispose()
with sqlite3.connect(STAGING) as database:
    assert database.execute("PRAGMA quick_check").fetchone() == ("ok",)
    assert not database.execute("PRAGMA foreign_key_check").fetchall()
    assert database.execute("SELECT count(*) FROM ideas").fetchone()[0] == 247
    assert database.execute("SELECT count(*) FROM ventures").fetchone()[0] == 5
backup_sqlite("sqlite:///" + str(STAGING), TARGET)
backup = TARGET.parent / "backups/2026-10-02-adopted.local.db"
backup_sqlite("sqlite:///" + str(TARGET), backup)
for path, digest in source_hashes.items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest
report = {
    "date": "2026-10-02",
    "target": str(TARGET),
    "backup": str(backup),
    "source_sha256": source_hashes,
    "source_files_unchanged": True,
    "merged_earlier_records": merged,
    "portfolio_collision_policy": (
        "Keep campaign default portfolio; preserve all earlier venture records and IDs"
    ),
    "import": result,
    "idea_count": 247,
    "venture_count": 5,
}
(OUT / "adoption-result.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
