from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
import pandas as pd
from src.sku_mapper import SKUMapper

app = FastAPI(title="CSTE WMS API")
mapper = SKUMapper()

@app.post("/map_file")
async def map_file(f: UploadFile = File(...)):
    df = pd.read_csv(f.file)
    mapped = mapper.auto_map(df)
    return StreamingResponse(mapped.to_csv(index=False),
                             media_type="text/csv",
                             headers={"Content-Disposition":"attachment; filename=mapped.csv"})

@app.get("/", response_class=HTMLResponse)
def docs_redirect():
    return '<meta http-equiv="refresh" content="0; URL=/docs" />'
