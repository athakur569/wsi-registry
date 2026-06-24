"""SlideRegistry: in-memory slide manifest with query and export."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

import pandas as pd


@dataclass
class SlideRecord:
    slide_id: str
    cohort: str
    label: int
    institution: str
    split: str
    path: str = ""
    extra: dict = field(default_factory=dict)


class SlideRegistry:
    """In-memory registry of WSI slide metadata.

    Args:
        records: Optional initial list of SlideRecord.
    """

    def __init__(self, records: list[SlideRecord] | None = None) -> None:
        self._records: list[SlideRecord] = records or []

    def add(self, record: SlideRecord) -> None:
        self._records.append(record)

    def query(
        self,
        cohort: str | None = None,
        split: str | None = None,
        institution: str | None = None,
        label: int | None = None,
    ) -> list[SlideRecord]:
        results = self._records
        if cohort is not None:
            results = [r for r in results if r.cohort == cohort]
        if split is not None:
            results = [r for r in results if r.split == split]
        if institution is not None:
            results = [r for r in results if r.institution == institution]
        if label is not None:
            results = [r for r in results if r.label == label]
        return results

    def __len__(self) -> int:
        return len(self._records)

    def __iter__(self) -> Iterator[SlideRecord]:
        return iter(self._records)

    def to_dataframe(self) -> pd.DataFrame:
        rows = [
            {
                "slide_id": r.slide_id,
                "cohort": r.cohort,
                "label": r.label,
                "institution": r.institution,
                "split": r.split,
                "path": r.path,
            }
            for r in self._records
        ]
        return pd.DataFrame(rows)

    def to_csv(self, path: str | Path) -> None:
        self.to_dataframe().to_csv(path, index=False)

    @classmethod
    def from_csv(cls, path: str | Path) -> "SlideRegistry":
        df = pd.read_csv(path)
        records = [
            SlideRecord(
                slide_id=row["slide_id"],
                cohort=row["cohort"],
                label=int(row["label"]),
                institution=row["institution"],
                split=row["split"],
                path=str(row.get("path", "")),
            )
            for _, row in df.iterrows()
        ]
        return cls(records)
