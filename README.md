# NexTrack

Small FastAPI service that turns a Google Sheet into a lightweight CRM API.
The sheet, `CRM_database`, has four worksheets: `Users`, `Customers`,
`Products`, and `Bills`. NexTrack exposes CRUD and search endpoints on top of
those tabs using [gspread](https://gspread.readthedocs.io/).

Built as a learning project for wiring a Python API to a spreadsheet backend
before graduating to a real database.

## Endpoints

Users, Customers, and Products all expose the same four operations:

- `POST /{collection}/` create
- `GET /{collection}/{id}` fetch by id
- `PUT /{collection}/{id}` overwrite
- `DELETE /{collection}/{id}` remove

Bills and search:

- `POST /bills/` creates a bill and computes the total from the referenced
  product rows (price plus tax, times quantity, per line)
- `GET /search/users/?query=...`, `/search/customers/`, `/search/products/`
  case-insensitive name search
- `GET /customers/{id}/purchase_history` all bills for a given customer

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn gspread oauth2client pydantic
```

1. Create a Google Cloud service account with access to the target sheet.
2. Share the sheet with the service-account email address.
3. Drop the JSON key file next to `main.py` and update the filename reference
   in `main.py` if it differs from `nextrack-*.json`.

## Running

```bash
uvicorn main:app --reload
```

API at `http://localhost:8000`, interactive docs at
`http://localhost:8000/docs`.

## Notes

- `main.py` loads the credentials file from a hard-coded filename. Do not
  commit a real service-account key to source control; load it from an
  environment variable or a secret manager if you plan to deploy this
  anywhere.
- Worksheet names are case-sensitive. The sheet must have tabs named exactly
  `Users`, `Customers`, `Products`, and `Bills`.
