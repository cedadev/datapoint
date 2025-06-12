# Release Notes for v0.5.0

## Added Asset Script
- Migrated Mapper into Asset Module
- Added BasicAsset as start point for Individual Objects.
- Added (Non-implemented) open-asset function to allow non-cloud assets to be downloaded/opened.

## Client Class
- Added Nested collections support - Auto-adds any nested collections under the searched collection.
- Added `data-selection` parameter to search.
- Added `apply-search-to-xarray` switch to search. Default is True.
- Added `search-terms` parameter to collect all pystac search options for further use.

## Search Class
- Added `search-terms` to meta inherited by sub-objects.
- Added `data-selection` property to be passed directly to sub-objects.

## Item Class
- Added `data-selection` property to be passed directly to cloud product objects.
- Added `get_data_files` function to find all non-cloud assets as a list.
- Added `get_assets` function to obtain a dict of BasicAsset objects.

## Product Class
- Added `prepare-data` switch to open dataset. Default is True which applies data selections and pystac search options where possible.
- Added `prepare-data` function which supports the following Single-Search selections:
    - `intersects` - from pystac intersection search.
    - `datetime` - from pystac datetime search.
    - `variable` - in data selection.
    - `sel` - custom selection from data selection.
    - See the new documentation `How to Use Datapoint >> Single-Search Selections`.