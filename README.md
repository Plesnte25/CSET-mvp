# Warehouse Management MVP — SKU Mapping & Sales Analytics

An end-to-end warehouse tooling MVP for sellers who need to reconcile marketplace
SKUs against their own internal MSKU catalogue and get quick sales insight without
standing up a full ERP.

It does three things:

1. **Maps SKUs → MSKUs** from an uploaded mapping file, with format validation and
   a per-run audit log of every lookup (matched, missing, or malformed).
2. **Cleans & enriches raw marketplace sales exports**, auto-detecting the SKU
   column, tagging each row with its MSKU, and reporting match/miss counts.
3. **Surfaces the result three ways**: a Streamlit web dashboard (KPIs, charts,
   optional natural-language querying over the data via PandasAI), a REST API
   (`/map_file`) for programmatic use, and a standalone Tkinter desktop app for
   fully offline use.

Processed data can optionally be pushed to [Baserow](https://baserow.io) — chosen
over Airtable for its generous free tier, self-host option, and REST API parity
(NocoDB and Teable.io were also evaluated).

## Architecture

```
src/
├── sku_mapper.py     # Core mapping engine: validation, logging, sales processing
├── baserow_client.py # Push processed rows to a Baserow table
├── streamlit_app.py  # Web dashboard — KPIs, charts, natural-language queries
├── api.py            # FastAPI endpoint: POST mapping + sales -> mapped CSV
├── desktop_gui.py     # Tkinter desktop app — offline SKU mapping
└── text2sql.py        # CLI: ask questions over processed data via a SQL agent
```

## Quick start

```bash
git clone https://github.com/Plesnte25/CSET-mvp.git
cd CSET-mvp
cp .env.example .env   # fill in BASEROW_API_TOKEN / OPENAI_API_KEY if you want those features
docker compose up --build
```

- Web dashboard: http://localhost:8501
- API docs: http://localhost:8000/docs
- Baserow (self-hosted, optional): http://localhost:8080

Or run locally without Docker:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run src/streamlit_app.py
```

Try it immediately with the bundled synthetic demo data (no real customer data —
see [Data](#data) below):

- Mapping file: `sample_data/sample_mapping.csv`
- Sales file: `sample_data/sample_sales.csv`

Upload both in the sidebar and click **Process** — one row (`UNKNOWN-SKU-999`) is
deliberately unmapped so you can see the "missing" count and logging behave
correctly on real-world messy data.

### Desktop app (offline)

```bash
python src/desktop_gui.py
```

### Natural-language queries over processed exports

```bash
python src/text2sql.py
```
Requires `OPENAI_API_KEY` in `.env`. Loads every CSV in `src/processed/` into
DuckDB and lets you ask questions in plain English via a LangChain SQL agent.

## Tech stack

Python, pandas, Streamlit, FastAPI, Tkinter, DuckDB, LangChain, PandasAI, Baserow,
Docker.

## Data

The `data/` folder used during development is **not committed** — it previously
held a downloaded practice dataset that turned out to contain real customer names
and addresses, which has since been purged from this repo's history. `sample_data/`
contains hand-written synthetic rows only, safe to commit and share.

## Status

Functionally complete per-module; not yet verified end-to-end in a live
environment (Docker build + full request cycle) after this restructure — treat as
"should work, needs one local smoke-test pass" rather than "confirmed working."
