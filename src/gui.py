import streamlit as st
import pandas as pd
from utils import load_any
from sku_mapper import SKUMapper
from pathlib import Path

st.set_page_config("WMS – SKU Mapper", layout="wide")
mapper = SKUMapper()

st.sidebar.header("Upload sales or mapping files")
uploaded = st.sidebar.file_uploader("Drop CSV/XLSX", accept_multiple_files=True)

if uploaded:
    dfs = [load_any(f).assign(_file=f.name) for f in uploaded]
    df = pd.concat(dfs)
    st.write("Raw data", df.head())

    mapped = mapper.auto_map(df, sku_col="FNSKU")
    st.write("After mapping", mapped.head())

    st.download_button("Download mapped CSV",
    mapped.to_csv(index=False), "mapped.csv")

st.sidebar.markdown("---")
st.sidebar.header("Add / correct mapping")
sku = st.sidebar.text_input("SKU")
msku = st.sidebar.text_input("MSKU")
if st.sidebar.button("Save mapping") and sku and msku:
    mapper.register(sku, msku)
    st.sidebar.success(f"Linked {sku} → {msku}")