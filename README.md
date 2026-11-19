# da-eplanning-nsw

Downloads development application (DA) data from the [NSW Planning Portal](https://www.planningportal.nsw.gov.au/) open data API and saves it as a CSV.

`ExtractDA.py` fetches every determined DA in a date range, works through all pages of results, removes duplicates and writes `development-applications.csv`.

## Setup

Requires Python 3.

```bash
python -m venv .venv
.venv\Scripts\activate.bat        # Windows (cmd, not PowerShell)
source .venv/bin/activate         # macOS / Linux
pip install -r requirements.txt
```

In VS Code, open the folder, create the venv in the terminal (Ctrl+\`), and select it as the interpreter when prompted (or Ctrl+P → `Python: Select interpreter`).

## Usage

```bash
python ExtractDA.py
```

Settings are in the `CONFIG` block at the top of `ExtractDA.py`:

| Setting | Default | Notes |
|---|---|---|
| `determination_date_from` / `_to` | `2022-01-01` / `2022-06-30` | Determination date range |
| `development_categories` | All five | Fetched one category at a time |
| `base_filters` | Determined DAs | Any filter from the API docs |
| `results_per_page` | `1000` | |
| `output_filename` | `development-applications.csv` | |

Large date ranges take a while. The script makes one request per page and pauses briefly between requests.

## The API

Base URL: `https://api.apps1.nsw.gov.au/eplanning/data/v0/`. It's public and doesn't need a key.

| Endpoint | Data | Docs |
|---|---|---|
| `OnlineDA` | Development applications | `Online DA API v2.0.pdf` |
| `OnlineCDC` | Complying development certificates | `Online CDC API v2.0.pdf` |
| `OnlineCC` | Construction certificates | Undocumented (see below) |

All endpoints are `GET` requests. Paging and filters go in the request headers, not the query string:

```bash
curl -H 'pageSize: 10' -H 'pageNumber: 1' \
     -H 'filters: {"filters":{"CouncilName":["PENRITH CITY COUNCIL"]}}' \
     https://api.apps1.nsw.gov.au/eplanning/data/v0/OnlineDA
```

Responses include `TotalCount`, `TotalPages` and an `Application` array.

### Things the PDFs don't tell you

Tested in November 2026:

- **`DevelopmentCategory` is optional.** Leaving it out returns slightly more records (26,538 vs 26,454 for H1 2022). The extra records are DAs that fall outside the five categories, so filtering by category drops them.
- **A `filters` header is required.** Without it the API returns `400`. To fetch everything, send `{"filters":{}}`.
- **`OnlineCC` exists.** It isn't in the official docs, so it could change without notice. It works like the other endpoints. `CouncilName`, `ApplicationStatus`, `LodgementDate*` and `DeterminationDate*` filters work. Application numbers start with `CFT-`. Records include building class, existing/proposed floor area, builder name and current/proposed building use. Valid `ApplicationType`/`ApplicationStatus` values are not yet known.

## License

Apache 2.0
