# Bangkok condo map

[繁體中文](README.md)｜English｜[ภาษาไทย](README.th.md)

An interactive map and property research tool for Bangkok condos. Explore condo projects, transit stations, listing samples with available source links, and estimated rental yields.

## Features

- Browse Bangkok condos and BTS, MRT, Airport Rail Link, and boat stations on the map.
- Filter and sort by bedrooms, total price, sale or rent price per square metre, annual yield, completion year, low-rise status, and transit distance.
- Review project completion details, coordinate sources, listing samples, and available original listing links.
- Estimate annual yield from the lowest one-bedroom or two-bedroom sale and rent samples. If their areas differ by more than 2 m², estimate rent using the lowest rent per square metre and the lowest-priced sale sample's area.
- Load condos around the current map view and estimate walking distance to transit.

## Data and estimates

Project data is compiled from sources including Hipflat, PropertyHub, DDproperty, and OpenStreetMap. Available source links are shown with condo details. Coordinate, listing, and completion-year coverage varies by project. Prices and yields are calculated from available samples; follow the source links to verify current availability. Yield estimates are not investment advice.

Map data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright).

## Run locally

The website is a static frontend. Built files are in `dist/`. From the project root, run:

```powershell
cd dist
py -m http.server 4173
```

Then open <http://127.0.0.1:4173/>.

## Build data

`scripts/` contains Python scripts for browser data, transit stations, walking routes, and data audits. Follow the instructions in the relevant script when updating data, then run:

```powershell
py scripts/build_fast_browser_data.py
```

Site deployment settings are in `.openai/hosting.json`; the static directory is `dist/`.
