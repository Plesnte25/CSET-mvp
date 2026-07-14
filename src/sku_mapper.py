import pandas as pd
import re, csv, os, io
from datetime import datetime
from pathlib import Path


class SKUMapper:
    """Handles SKU -> MSKU mappings and sales data processing."""

    def __init__(self):
        self.mapping_dict: dict[str, str] = {}
        self.regex = re.compile(r"^[A-Z0-9_-]+$")
        self.processed_dir = Path(__file__).with_name("processed")
        self.processed_dir.mkdir(exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.processed_dir / f"sku_mapping_log_{ts}.csv"

    # ---------- Core Mapping Methods ----------
    def load_mappings(self, file_path: str | os.PathLike, sheet_name: int | str = 0):
        """Load mapping file (CSV/Excel). Expects 1st col = SKU, 2nd col = MSKU."""
        filename = getattr(file_path, "name", str(file_path))
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            except ValueError:
                if isinstance(sheet_name, str):
                    xl = pd.ExcelFile(file_path)
                    matches = [s for s in xl.sheet_names if s.lower() == sheet_name.lower()]
                    if matches:
                        df = pd.read_excel(file_path, sheet_name=matches[0])
                    else:
                        raise
        if df.shape[1] < 2:
            raise ValueError("Mapping file must have at least two columns: SKU & MSKU")
        sku_col, msku_col = df.columns[:2]
        for sku, msku in zip(df[sku_col].astype(str).str.strip(), df[msku_col].astype(str).str.strip()):
            if not self.validate_sku(sku):
                self.log_mapping(sku, "InvalidFormat")
                continue
            self.mapping_dict[sku] = msku

    def validate_sku(self, sku: str) -> bool:
        return bool(self.regex.fullmatch(str(sku).strip()))

    def add_combo(self, sku_list: list[str], msku: str):
        for sku in sku_list:
            self.mapping_dict[sku] = msku

    def map_sku(self, sku: str) -> str | None:
        sku = str(sku).strip()
        msku = self.mapping_dict.get(sku)
        self.log_mapping(sku, msku if msku is not None else "Missing")
        return msku

    def log_mapping(self, sku: str, msku: str):
        header = not self.log_file.exists()
        with open(self.log_file, "a", newline="") as f:
            w = csv.writer(f)
            if header:
                w.writerow(["timestamp", "SKU", "MSKU"])
            w.writerow([datetime.now().isoformat(), sku, msku])

    # ---------- Sales Processing ----------
    def process_sales(self, sales_file: str | os.PathLike | io.BytesIO):
        filename = getattr(sales_file, "name", str(sales_file))
        ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
        try:
            if ext == "csv":
                try:
                    df = pd.read_csv(sales_file)
                except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError, ValueError):
                    if hasattr(sales_file, "seek"):
                        sales_file.seek(0)
                    df = pd.read_csv(sales_file, engine="python", sep=None, encoding="utf-8", on_bad_lines="skip")
            elif ext in ("xlsx", "xls", "xlsm"):
                df = pd.read_excel(sales_file, engine="openpyxl")
            else:
                try:
                    df = pd.read_csv(sales_file)
                except Exception:
                    if hasattr(sales_file, "seek"):
                        sales_file.seek(0)
                    df = pd.read_excel(sales_file, engine="openpyxl")
        except Exception as e:
            raise ValueError(f"Failed to read sales file `{filename}`: {e}") from e

        possible_cols = [c for c in df.columns if "sku" in c.lower()]
        if not possible_cols:
            raise ValueError("Could not auto-detect SKU column in sales file")
        sku_col = possible_cols[0]

        df["MSKU"] = df[sku_col].apply(lambda x: self.map_sku(str(x)))
        mapped = int(df["MSKU"].notna().sum())
        missing = int(df["MSKU"].isna().sum())

        out_name = f"{Path(filename).stem}_WITH_MSKU_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        out_path = self.processed_dir / out_name
        df.to_csv(out_path, index=False)

        return df, mapped, missing
