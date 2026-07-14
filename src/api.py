from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from src.sku_mapper import SKUMapper

app = FastAPI(title="WMS SKU Mapping API")


@app.post("/map_file")
async def map_file(mapping: UploadFile = File(...), sales: UploadFile = File(...)):
    """Maps SKUs -> MSKUs in a sales file using an uploaded mapping file."""
    mapper = SKUMapper()
    mapping.file.name = mapping.filename or "mapping.csv"
    mapper.load_mappings(mapping.file)

    sales.file.name = sales.filename
    processed_df, mapped, missing = mapper.process_sales(sales.file)

    return StreamingResponse(
        iter([processed_df.to_csv(index=False)]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=mapped.csv",
            "X-Mapped-Count": str(mapped),
            "X-Missing-Count": str(missing),
        },
    )


@app.get("/", response_class=HTMLResponse)
def docs_redirect():
    return '<meta http-equiv="refresh" content="0; URL=/docs" />'
