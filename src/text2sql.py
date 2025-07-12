# src/text2sql.py
from langchain.agents import create_sql_agent
from langchain.utilities import SQLDatabase
import duckdb, pandas as pd

def export_baserow_to_duckdb(csv_dir="data/baserow_exports"):
    con = duckdb.connect("analytics.duckdb")
    for csv in Path(csv_dir).glob("*.csv"):
        df = pd.read_csv(csv)
        tbl = csv.stem
        con.register(tbl, df)  # view
        df.to_parquet(f"{tbl}.parquet")  # optional
    return con

db = SQLDatabase.from_uri("duckdb://analytics.duckdb")
agent = create_sql_agent(llm="gpt-4o-mini", db=db, verbose=True)

while True:
    q = input("Ask WMS › ")
    print(agent.run(q))
