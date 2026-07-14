import os
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from sku_mapper import SKUMapper
from baserow_client import push_dataframe

load_dotenv()

st.set_page_config(page_title="WMS Sales Processor", layout="wide")
st.title("Warehouse Sales Processor")

# ---------- Sidebar: Mapping upload ----------
st.sidebar.header("Step 1 · Upload SKU Mapping")
mapping_file = st.sidebar.file_uploader("Mapping (CSV/Excel)", type=["csv", "xlsx", "xls"])
mapper = SKUMapper()
if mapping_file:
    is_excel = mapping_file.name.lower().endswith(("xls", "xlsx"))
    if is_excel:
        xl = pd.ExcelFile(mapping_file)
        sheet = st.sidebar.selectbox("Pick sheet", xl.sheet_names, index=0)
        mapping_file.seek(0)
        mapper.load_mappings(mapping_file, sheet_name=sheet)
    else:
        mapper.load_mappings(mapping_file)
    st.sidebar.success(f"{len(mapper.mapping_dict)} mappings loaded")

# ---------- Sidebar: Sales upload ----------
st.sidebar.header("Step 2 · Upload Raw Sales")
sales_file = st.sidebar.file_uploader("Sales (CSV/Excel)", type=["csv", "xlsx", "xls"])

if sales_file and st.sidebar.button("Process"):
    processed_df, mapped, missing = mapper.process_sales(sales_file)
    st.success(f"{mapped} SKUs mapped, {missing} missing")

    st.subheader("Preview")
    st.dataframe(processed_df.head(200), use_container_width=True)

    # ---------- KPI Cards ----------
    st.subheader("Key Metrics")
    col1, col2 = st.columns(2)
    col1.metric("Total Orders", f"{len(processed_df):,}")
    if "Total" in processed_df.columns:
        col2.metric("Avg. Order Value", f"{processed_df['Total'].mean():,.2f}")

    # ---------- Charts ----------
    if "MSKU" in processed_df.columns:
        fig = px.bar(
            processed_df.groupby("MSKU")["Quantity"].sum().reset_index(),
            x="MSKU",
            y="Quantity",
            title="Sales by Product (Quantity)",
        )
        st.plotly_chart(fig, use_container_width=True)

    if "Date" in processed_df.columns:
        processed_df["Date"] = pd.to_datetime(processed_df["Date"], errors="coerce")
        monthly = (
            processed_df.dropna(subset=["Date"])
            .groupby(processed_df["Date"].dt.to_period("M"))["Quantity"]
            .sum()
            .reset_index()
        )
        monthly["Date"] = monthly["Date"].astype(str)
        fig2 = px.line(monthly, x="Date", y="Quantity", title="Monthly Sales Trend")
        st.plotly_chart(fig2, use_container_width=True)

    # ---------- Push to Baserow ----------
    st.subheader("Persist")
    table_id = st.text_input("Baserow Table ID")
    if st.button("Save to Baserow") and table_id:
        push_dataframe(table_id, processed_df)
        st.success("Data pushed to Baserow")

    # ---------- PandasAI natural-language layer ----------
    if os.getenv("OPENAI_API_KEY"):
        from pandasai import SmartDataframe
        from pandasai_openai import OpenAI

        st.subheader("Ask your data (natural language)")
        smart_df = SmartDataframe(processed_df, config={"llm": OpenAI(api_token=os.getenv("OPENAI_API_KEY"))})
        query = st.text_input("e.g. Show top 10 products by sales last month")
        if query:
            st.write(smart_df.chat(query))
    else:
        st.info("Set OPENAI_API_KEY in .env to enable natural-language analysis.")
