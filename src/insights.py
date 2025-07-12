import streamlit as st, sqlalchemy as sa
from llama_index import VectorStoreIndex, SQLDatabase, ServiceContext
from llama_index.indices.struct_store.sql_query import NLSQLTableQueryEngine

st.title("📊 Warehouse Insights – Ask me anything")

db_uri = st.secrets["db_uri"]   # Postgres replica of Baserow
engine = sa.create_engine(db_uri)
sql_db = SQLDatabase(engine)

if "qa" not in st.session_state:
    llm_ctx = ServiceContext.from_defaults()
    st.session_state.qa = NLSQLTableQueryEngine(sql_db, service_context=llm_ctx)

q = st.text_input("Natural language question")
if q:
    res = st.session_state.qa.query(q)
    st.write(res.response)
    st.table(res.metadata["result"])
