"""CohortSummary: label and institution balance checks."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .registry import SlideRegistry


@dataclass
class CohortSummaryResult:
    cohort: str
    total: int
    label_counts: dict[int, int] = field(default_factory=dict)
    institution_counts: dict[str, int] = field(default_factory=dict)
    split_counts: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


class CohortSummary:
    """Generate per-cohort balance reports from a SlideRegistry.

    Args:
        registry: Populated SlideRegistry.
    """

    def __init__(self, registry: SlideRegistry) -> None:
        self.registry = registry

    def summarize(self, cohort: str) -> CohortSummaryResult:
        records = self.registry.query(cohort=cohort)
        result = CohortSummaryResult(cohort=cohort, total=len(records))
        for r in records:
            result.label_counts[r.label] = result.label_counts.get(r.label, 0) + 1
            result.institution_counts[r.institution] = (
                result.institution_counts.get(r.institution, 0) + 1
            )
            result.split_counts[r.split] = result.split_counts.get(r.split, 0) + 1

        # warn if any split is missing a class
        for split_name in ("train", "val", "test"):
            split_records = [r for r in records if r.split == split_name]
            labels_present = {r.label for r in split_records}
            if split_records and len(labels_present) < 2:
                result.warnings.append(
                    f"Split '{split_name}' has only one class present: {labels_present}"
                )
        return result

    def summarize_all(self) -> list[CohortSummaryResult]:
        cohorts = {r.cohort for r in self.registry}
        return [self.summarize(c) for c in sorted(cohorts)]

    def to_dataframe(self) -> pd.DataFrame:
        rows = []
        for s in self.summarize_all():
            rows.append(
                {
                    "cohort": s.cohort,
                    "total": s.total,
                    "n_pos": s.label_counts.get(1, 0),
                    "n_neg": s.label_counts.get(0, 0),
                    "n_institutions": len(s.institution_counts),
                    "warnings": "; ".join(s.warnings) if s.warnings else "",
                }
            )
        return pd.DataFrame(rows)
