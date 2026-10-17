"""Create lean browser copies of PropertyHub feeds by omitting unused listing arrays.

Run after refreshing the source feeds:
    python scripts/build_browser_data.py
The source files stay intact for research and future refreshes.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def load_array(filename: str, global_name: str) -> list[dict]:
    text = (DIST / filename).read_text(encoding="utf-8")
    prefix = f"window.{global_name} = "
    if not text.startswith(prefix):
        raise ValueError(f"Unexpected data format in {filename}")
    return json.loads(text[len(prefix):].strip().removesuffix(";"))


def strip_samples(value):
    if isinstance(value, list):
        return [strip_samples(item) for item in value]
    if isinstance(value, dict):
        return {key: strip_samples(item) for key, item in value.items() if key != "samples"}
    return value


if __name__ == "__main__":
    projects = load_array("bangkok-propertyhub.js", "BANGKOK_PROPERTYHUB_PROJECTS")
    summaries = {int(row["id"]): row for row in load_array("bangkok-propertyhub-city-summaries.js", "BANGKOK_PROPERTYHUB_CITY_SUMMARIES")}
    for project in projects:
        summary = summaries.get(int(project["id"]), {})
        for market in ("sale", "rent"):
            if summary.get(market):
                project[market] = summary[market]
    browser_fields = {
        "address", "area", "beds", "completedYear", "fee", "floors", "hipflatSummary", "id", "lat", "lng",
        "locationSourceName", "locationSourceUrl", "locationVerified", "nearestMrt", "propertyHubProjectId",
        "propertyHubProjectUrl", "propertyHubRentUrl", "propertyHubSaleUrl", "rent", "sale", "station", "units",
    }
    rows = strip_samples([{key: value for key, value in project.items() if key in browser_fields} for project in projects])
    output = "window.BANGKOK_PROPERTYHUB_PROJECTS = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n"
    target = DIST / "bangkok-propertyhub-map.js"
    target.write_text(output, encoding="utf-8")
    print(f"Combined browser feed → {target.name}: {target.stat().st_size:,} bytes")
