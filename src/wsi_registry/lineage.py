"""SplitLineage: verify that splits were generated from a known freeze hash."""

from __future__ import annotations

import json
from pathlib import Path


class SplitLineageError(Exception):
    pass


class SplitLineage:
    """Track and verify the freeze hash under which splits were created.

    Args:
        metadata_path: Path to split_metadata.json written at freeze time.
    """

    def __init__(self, metadata_path: str | Path) -> None:
        self.metadata_path = Path(metadata_path)
        self._meta: dict = {}
        if self.metadata_path.exists():
            with open(self.metadata_path) as fh:
                self._meta = json.load(fh)

    @property
    def recorded_hash(self) -> str | None:
        return self._meta.get("freeze_hash")

    @property
    def split_date(self) -> str | None:
        return self._meta.get("split_date")

    def verify(self, freeze_hash: str) -> None:
        """Raise SplitLineageError if the hash does not match the recorded value."""
        recorded = self.recorded_hash
        if recorded is None:
            raise SplitLineageError(
                "No freeze_hash in split metadata — splits were not created from a frozen set."
            )
        if recorded != freeze_hash:
            raise SplitLineageError(
                f"Hash mismatch: splits were generated from {recorded!r}, "
                f"current freeze is {freeze_hash!r}. Re-run splits or use the correct freeze."
            )

    @classmethod
    def record(
        cls,
        metadata_path: str | Path,
        freeze_hash: str,
        split_date: str,
        extra: dict | None = None,
    ) -> "SplitLineage":
        """Write a new metadata file and return the lineage object."""
        meta = {"freeze_hash": freeze_hash, "split_date": split_date, **(extra or {})}
        path = Path(metadata_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as fh:
            json.dump(meta, fh, indent=2)
        return cls(path)
