"""CLI: ask natural-language questions over the processed sales data via a SQL agent."""
from pathlib import Path
import duckdb, pandas as pd
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase


def export_to_duckdb(csv_dir="processed", db_path="analytics.duckdb"):
    con = duckdb.connect(db_path)
    for csv in Path(csv_dir).glob("*.csv"):
        df = pd.read_csv(csv)
        con.register(csv.stem, df)
    return con, db_path


if __name__ == "__main__":
    _, db_path = export_to_duckdb()
    db = SQLDatabase.from_uri(f"duckdb:///{db_path}")
    agent = create_sql_agent(llm="gpt-4o-mini", db=db, verbose=True)

    while True:
        q = input("Ask WMS > ")
        if q.lower() in {"exit", "quit"}:
            break
        print(agent.run(q))
