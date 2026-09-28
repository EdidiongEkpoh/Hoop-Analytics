import time
import pandas as pd
from sqlalchemy import create_engine
from extract import get_player_info, fetch_with_retry, stamp_run_metadata, load_to_postgres, NBA_DB_USER, NBA_DB_PASSWORD, NBA_DB_HOST, NBA_DB_PORT, NBA_DB_NAME

MISSING_PLAYER_IDS = [1642380, 1631457, 1643158, 1643016, 1642396, 1643052, 1642504, 1642468, 1641761, 1643060, 1642942, 1643257, 1642967,
1642490, 1642882, 1642955, 1642933, 1642933, 1643133, 1643018, 1631351, 1641869, 1641807, 1642362, 1642951, 1643253,
1642400, 1631174]  # pull the full list from the earlier "missing from dim_players" query
SEASON, LEAGUE_ID = "2025-26", "00"

engine = create_engine(f"postgresql://{NBA_DB_USER}:{NBA_DB_PASSWORD}@{NBA_DB_HOST}:{NBA_DB_PORT}/{NBA_DB_NAME}")
player_info_pull = get_player_info()

rows, still_failed = [], []
for pid in MISSING_PLAYER_IDS:
    try:
        rows.append(fetch_with_retry(player_info_pull['fetch_fn'], pid, LEAGUE_ID))
    except Exception as e:
        print(f"Still failing for {pid}: {e}")
        still_failed.append(pid)
    time.sleep(1.0)

if rows:
    batch_df = pd.concat(rows, ignore_index=True)
    batch_df = stamp_run_metadata(batch_df, SEASON, LEAGUE_ID, "Regular Season", "player_info")
    load_to_postgres(batch_df, player_info_pull['table'], engine)
    print(f"Loaded {len(rows)} players.")
print(f"Still failed: {still_failed}")