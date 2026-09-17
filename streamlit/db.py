import os 
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

@st.cache_resource
def get_engine():
    user = os.environ.get("NBA_DB_USER")
    password = os.environ.get("NBA_DB_PASSWORD")
    host = os.environ.get("NBA_DB_HOST")
    port = os.environ.get("NBA_DB_PORT")
    name = os.environ.get("NBA_DB_NAME")

    sslmode = "disable" if host in ("localhost", "127.0.0.1") else "require"
    return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{name}?sslmode={sslmode}")

@st.cache_data(ttl=3600)
def run_query(sql: str, params: dict | None=None) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})

def available_seasons():
    df = run_query(
        "SELECT DISTINCT season FROM staging_marts.dim_standings ORDER BY season DESC"
    )
    return df['season'].tolist()