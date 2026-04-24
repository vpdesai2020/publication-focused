from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Markdown tables from an aggregate JSON file.")
    parser.add_argument("summary_json", type=Path)
    parser.add_argument("--output", type=Path, default=Path("paper/tables.md"))
    args = parser.parse_args()

    summary = json.loads(args.summary_json.read_text(encoding="utf-8"))
    lines = [
        "# Paper Tables",
        "",
        "## Repair Success by Strategy",
        "",
        "| Strategy | Trials | Success Rate | 95% CI | Mean Reduction | Functional Preservation |",
        "| --- | ---: | ---: | --- | ---: | ---: |",
    ]
    for strategy, row in sorted(summary.get("by_strategy", {}).items()):
        ci = row["repair_success_ci95"]
        lines.append(
            f"| {strategy} | {row['trials']} | {row['repair_success_rate']:.3f} | "
            f"[{ci[0]:.3f}, {ci[1]:.3f}] | {row['mean_vulnerability_reduction']:.3f} | "
            f"{row['functional_preservation_rate']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "These tables are generated from local results. Fixture runs validate the pipeline only and are not paper evidence.",
            "",
        ]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(str(args.output))


if __name__ == "__main__":
    main()

