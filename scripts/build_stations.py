"""Create the named Bangkok rapid-transit station layer from OSM data."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = pathlib.Path(r"C:\Users\j654v\Desktop\codex\condo_research\bangkok\osm-mrt-stations.json")
elements = json.loads(SOURCE.read_text(encoding="utf-8"))["elements"]
rows = []
for item in elements:
    tags = item.get("tags", {})
    name = tags.get("name:en") or tags.get("name")
    refs = (tags.get("ref") or "").split(";")
    if not name or not refs:
        continue
    for ref in refs:
        if ref.startswith("BL"):
            line = "MRT Blue Line"
        elif ref.startswith("PP"):
            line = "MRT Purple Line"
        elif ref.startswith("PK"):
            line = "MRT Pink Line"
        elif ref.startswith("YL"):
            line = "MRT Yellow Line"
        elif ref.startswith(("N", "E")):
            line = "BTS Sukhumvit Line"
        elif ref.startswith(("S", "W")) or ref == "CEN":
            line = "BTS Silom Line"
        elif ref.startswith("A"):
            line = "Airport Rail Link"
        else:
            line = "Bangkok Rapid Transit"
        rows.append({
            "id": ref,
            "name": name,
            "lat": item["lat"],
            "lng": item["lon"],
            "line": line,
            "sourceUrl": f"https://www.openstreetmap.org/node/{item['id']}",
        })
# OSM has several mapped nodes for some platforms or station entrances. Keep
# the first station node per route reference so each station is mapped once.
by_ref = {}
for row in rows:
    by_ref.setdefault(row["id"], row)
rows = sorted(by_ref.values(), key=lambda row: (row["line"], row["id"]))
out = ROOT / "dist/stations.js"
out.write_text("window.MRT_STATIONS = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
print(json.dumps({"count": len(rows), "lines": sorted({r["line"] for r in rows}), "output": str(out)}, ensure_ascii=False))
