"""CLI entrypoint for wsi-registry."""

from __future__ import annotations

import argparse
import sys

from .registry import SlideRegistry
from .cohort_summary import CohortSummary


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="wsi-registry",
        description="Query and summarize WSI slide manifests.",
    )
    sub = parser.add_subparsers(dest="command")

    p_summary = sub.add_parser("summary", help="Print cohort balance summary")
    p_summary.add_argument("manifest", help="Path to manifest CSV")
    p_summary.add_argument("--cohort", help="Filter to one cohort")

    p_query = sub.add_parser("query", help="List slides matching filters")
    p_query.add_argument("manifest", help="Path to manifest CSV")
    p_query.add_argument("--cohort")
    p_query.add_argument("--split")
    p_query.add_argument("--institution")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    reg = SlideRegistry.from_csv(args.manifest)

    if args.command == "summary":
        cs = CohortSummary(reg)
        df = cs.to_dataframe()
        if hasattr(args, "cohort") and args.cohort:
            df = df[df["cohort"] == args.cohort]
        print(df.to_string(index=False))

    elif args.command == "query":
        results = reg.query(
            cohort=getattr(args, "cohort", None),
            split=getattr(args, "split", None),
            institution=getattr(args, "institution", None),
        )
        for r in results:
            print(f"{r.slide_id}\t{r.cohort}\t{r.split}\t{r.institution}\t{r.label}")


if __name__ == "__main__":
    main()
