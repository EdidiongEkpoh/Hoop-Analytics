'''
Gives app access to the database and reads just the marts schema.

Includes two cached runners so completed seasons are never altered. Current
season data refreshes hourly.
'''
import os 
from decimal import Decimal 
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL 

load_dotenv()

LEAGUE_ID = "00"
MARTS_SCHEMA = os.environ.get("NBA_MARTS_SCHEMA", "marts")
STATIC_TTL = 24 * 3600
LIVE_TTL = 3600

def table(name):
    return f"{MARTS_SCHEMA}.{name}"

@st.cache_resource
def get_engine():
    host = os.environ.get("NBA_DB_HOST")
    port = os.environ.get("NBA_DB_PORT")
    url = URL.create(
        "postgresql+psycopg2",
        username=os.environ.get("NBA_DB_USER"),
        password=os.environ.get("NBA_DB_PASSWORD"),
        host=host,
        port=int(port) if port else None,
        database=os.environ.get("NBA_DB_NAME"),
        query={"sslmode":os.environ.get("NBA_DB_SSLMODE", "prefer")}
    )
    return create_engine(url, pool_pre_ping=True)

def _decimals_to_float(df):
    for col in df.select_dtypes(include="object").columns:
        sample = df[col].dropna()
        if not sample.empty and isinstance(sample.iloc[0], Decimal):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def _run(sql, params):
    with get_engine().connect() as conn:
        df = pd.read_sql(text(sql), conn, params=params or ())
    return _decimals_to_float(df)

@st.cache_data(ttl=STATIC_TTL, show_spinner=False)
def query_static(sql, params):
    return _run(sql, params)

@st.cache_data(ttl=LIVE_TTL, show_spinner=False)
def query_live(sql, params=None):
    return _run(sql, params)


