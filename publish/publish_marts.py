'''
Publishes the marts schema from the local warehouse to Neon so the live app can read it

Runs as the last task of the daily DAG, only after dbt has built and tested everything.
    1. Copy every marts table into a holding schema on Neon (marts_incoming).
    2. Check that each table's row count matches the source.
    3. Swap it in inside on transaction: marts -> marts_previous, marts_incoming -> marts, then drop marts_previous.
If anything fails before step 3, the live marts schema is untouched; the next run starts the holding schema over.
The app sees either yesterday's or today's data.
'''
import logging 
import os 
import sys 
import tempfile 
import time 
from sqlalchemy import MetaData, create_engine, text 
from sqlalchemy.engine import URL 

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger("publish")

SCHEMA = os.environ.get("NBA_MARTS_SCHEMA", "marts")
INCOMING = f"{SCHEMA}_incoming"
PREVIOUS = f"{SCHEMA}_previous"

def source_engine():
    port = os.environ.get("NBA_DB_PORT")
    url = URL.create(
        "postgresql+psycopg2",
        username=os.environ["NBA_DB_USER"],
        password=os.environ["NBA_DB_PASSWORD"],
        host=os.environ["NBA_DB_HOST"],
        port=int(port) if port else None,
        database=os.environ["NBA_DB_NAME"], 
        query={"sslmode": os.environ.get("NBA_DB_SSLMODE", "prefer")}
    )
    return create_engine(url, pool_pre_ping=True)

def target_engine():
    url = os.environ.get("NEON_DATABASE_URL")
    if not url:
        sys.exit("NEON_DATABASE_URL is not set; nothing to publish to.")
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg2://" + url[len("postgresql://"):]
    return create_engine(url, pool_pre_ping=True)

def copy_table(src, tgt, table):
    '''Stream one table with COPY through a temporary file. Returns the rows copied.'''
    cols = ", ".join(f'"{c.name}"' for c in table.columns)
    with tempfile.TemporaryFile() as buf:
        src_conn = src.raw_connection()
        try:
            with src_conn.cursor() as cur:
                cur.copy_expert(f'COPY (SELECT {cols} FROM "{SCHEMA}"."{table.name}") TO STDOUT' ,buf)
        finally:
            src_conn.close()
        buf.seek(0)
        tgt_conn = tgt.raw_connection()
        try:
            with tgt_conn.cursor() as cur:
                cur.copy_expert(f'COPY "{INCOMING}"."{table.name}" ({cols}) FROM STDIN', buf)
            tgt_conn.commit()
        finally:
            tgt_conn.close()
    with tgt.connect() as conn:
        return conn.execute(text(f'SELECT COUNT(*) FROM "{INCOMING}"."{table.name}"')).scalar()


def main():
    start = time.time() 
    src, tgt = source_engine(), target_engine()

    source = MetaData()
    source.reflect(bind=src, schema=SCHEMA)
    tables = sorted(source.tables.values(), key=lambda t: t.name)
    if not tables:
        sys.exit(f'No tables in "{SCHEMA}" on the local warehouse; refusing to publish an empty schema.')
    log.info(f"Publishing {len(tables)} tables from {SCHEMA}.")

    # 1. A fresh holding schema with the same table definitions.
    with tgt.begin() as conn:
        conn.execute(text(f'DROP SCHEMA IF EXISTS "{INCOMING}" CASCADE'))
        conn.execute(text(f'CREATE SCHEMA "{INCOMING}"'))
    incoming = MetaData()
    for t in tables:
        t.to_metadata(incoming, schema=INCOMING)
    incoming.create_all(tgt)

    # 2. Copy and verify each table
    with src.connect() as conn:
        expected = {t.name: conn.execute(text(f'SELECT COUNT(*) FROM "{SCHEMA}"."{t.name}"')).scalar() for t in tables}
    for t in tables:
        t0 = time.time() 
        got = copy_table(src, tgt, t)
        if got != expected[t.name]:
            raise RuntimeError(f"{t.name}: copied {got} rows, expected {expected[t.name]}. Live data left unchanged.")
        log.info(f"  {t.name}: {got:,} rows ({time.time() - t0:.1f}s)")

    # 3. Swap
    with tgt.begin() as conn:
        conn.execute(text("SET LOCAL lock_timeout = '60s'"))
        conn.execute(text(f'DROP SCHEMA IF EXISTS "{PREVIOUS}" CASCADE'))
        exists = conn.execute(text("SELECT 1 FROM information_schema.schemata WHERE schema_name = :s"), {"s": SCHEMA}).first()

        if exists:
            conn.execute(text(f'ALTER SCHEMA "{SCHEMA}" RENAME TO "{PREVIOUS}"'))
        conn.execute(text(f'ALTER SCHEMA "{INCOMING}" RENAME TO "{SCHEMA}"'))
        role = os.environ.get("NEON_APP_ROLE")
        if role:
            conn.execute(text(f'GRANT USAGE ON SCHEMA "{SCHEMA}" TO "{role}"'))
            conn.execute(text(f'GRANT SELECT ON ALL TABLES IN SCHEMA "{SCHEMA}" TO "{role}"'))

    with tgt.begin() as conn:
        conn.execute(text(f'DROP SCHEMA IF EXISTS "{PREVIOUS}" CASCADE'))

    log.info(f"Published {len(tables)} tables, {sum(expected.values()):,} rows, in {time.time() - start:.0f}s.")

if __name__ == "__main__":
    main()