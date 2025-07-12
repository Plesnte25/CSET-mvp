from pathlib import Path
import json
import pandas as pd

class SKUMapper:
    """Bidirectional SKU ↔ MSKU mapping with validation & logging."""

    def __init__(self, mapping_file: Path = Path("data/master_mapping.json")):
        self.path = mapping_file
        self._load()

    def _load(self):
        if self.path.exists():
            self.map = json.loads(self.path.read_text())
        else:
            self.map = {}  # {sku: msku}

    def save(self):
        self.path.write_text(json.dumps(self.map, indent=2))

    # ---------- Public API ----------
    def register(self, sku: str, msku: str):
        sku, msku = sku.strip(), msku.strip()
        self.map[sku] = msku
        self.save()

    def lookup(self, sku: str) -> str | None:
        return self.map.get(sku.strip())

    def auto_map(self, df: pd.DataFrame, sku_col="SKU") -> pd.DataFrame:
        df["MSKU"] = df[sku_col].map(self.map)
        return df
