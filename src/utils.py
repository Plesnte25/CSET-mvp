from pathlib import Path
import pandas as pd
import io

def load_any(src):
    """
    Accepts either a Path-like or a Streamlit UploadedFile / BytesIO object
    and returns a DataFrame.
    """
    # ---- Handle in-memory uploads ----------------------------------------
    if isinstance(src, (io.BufferedIOBase, io.BytesIO)) or hasattr(src, "read"):
        name = getattr(src, "name", "")  # UploadedFile has .name
        if name.endswith((".xlsx", ".xls")):
            return pd.read_excel(src)
        else:
            return pd.read_csv(src, low_memory=False)

    # ---- Handle paths on disk --------------------------------------------
    path = Path(src)
    if path.suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path, low_memory=False)
