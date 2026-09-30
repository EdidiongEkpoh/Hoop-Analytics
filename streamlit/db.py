import os 
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
CONST_STATS = ["fg_pct", "fg2_pct", "fg3_pct", "ft_pct", "fg3pr", "ftr",
                "ts_pct", "efg_pct", "usage", "oreb_pct", "dreb_pct", "reb_pct"
                , "assist_pct", "tov_pct", "stl_pct", "blk_pct", "net_rating"]

SCALED_STATS = ["pts", "reb", "ast", "stl", "blk", "tov"]

def combined_player_base(grain):
    per_x = {
        "Per Game": lambda col: col,
        "Per 36": lambda col: f"ROUND(({col}::NUMERIC / NULLIF(AVG(minutes), 0)) * 36, 2)",
        "Per 75": lambda col: f"ROUND(({col}::NUMERIC / NULLIF(AVG(possessions), 0)) * 75, 2)",
        "Per 100": lambda col: f"ROUND(({col}::NUMERIC / NULLIF(AVG(possessions), 0)) * 100, 2)",
    }[grain]

    return f'''
    SELECT player_id, season, league_id, season_type
        , COUNT(*) AS games_played
        , SUM(win_flag) AS wins
        , AVG(pts) AS pts_per_game
        , AVG(reb) AS rebs_per_game
        , AVG(ast) AS asts_per_game
        , AVG(stl) AS stls_per_game
        , AVG(blk) AS blks_per_game
        , AVG(tov) AS tovs_per_game
        , {per_x("AVG(pts)")} AS pts_scaled
        , {per_x("AVG(reb)")} AS reb_scaled
        , {per_x("AVG(ast)")} AS ast_scaled
        , {per_x("AVG(stl)")} AS stl_scaled
        , {per_x("AVG(blk)")} AS blk_scaled
        , {per_x("AVG(tov)")} AS tov_scaled
        , AVG(minutes) AS minutes_per_game
        , AVG(possessions) AS possessions_per_game 
        , AVG(fg_pct) AS fg_pct
        , AVG(fg2_pct) AS fg2_pct
        , AVG(fg3_pct) AS fg3_pct 
        , AVG(ft_pct) AS ft_pct
        , AVG(ftr) AS ftr
        , AVG(fg3pr) AS fg3pr
        , AVG(ts_pct) AS ts_pct
        , AVG(efg_pct) AS efg_pct
        , AVG(usage) AS usage
        , AVG(oreb_pct) AS oreb_pct
        , AVG(dreb_pct) AS dreb_pct
        , AVG(reb_pct) AS reb_pct 
        , AVG(assist_pct) AS assist_pct
        , AVG(stl_pct) AS stl_pct
        , AVG(blk_pct) AS blk_pct
        , AVG(tov_pct) AS tov_pct 
        , AVG(net_rating) AS net_rating
    FROM staging_staging.int_player_games_with_opponent
    WHERE season = :season
        AND league_id = :league_id
        AND season_type = :season_type
    GROUP BY 1, 2, 3, 4
    '''

def combined_player_query(grain):
    return f'''
        WITH combined AS ({combined_player_base(grain)})
        SELECT c.*
            , c.ts_pct - lsa.league_ts_pct AS relative_ts_pct
        FROM combined c
        LEFT JOIN staging_staging.int_league_season_averages lsa ON lsa.season = c.season
            AND lsa.season_type = c.season_type
            AND lsa.league_id = c.league_id
        WHERE c.player_id = :player_id
            '''

def combined_eligible_players(grain):
    return f'''
    WITH combined AS ({combined_player_base(grain)})
        , eligible AS (
            SELECT c.*
            FROM combined c 
            JOIN staging_staging.int_player_eligibility e ON e.player_id = c.player_id
                AND e.season = c.season
                AND e.season_type = c.season_type
                AND e.league_id = c.league_id
            WHERE e.meets_min_games_threshold = TRUE
        )
        SELECT e.*
            , dp.player_name
            , dp.current_team_id
            , dp.current_team_name
            , e.ts_pct - lsa.league_ts_pct AS relative_ts_pct
        FROM eligible e
        LEFT JOIN staging_marts.dim_players dp ON dp.player_id = e.player_id
        LEFT JOIN staging_staging.int_league_season_averages lsa ON lsa.season = e.season 
            AND lsa.league_id = e.league_id
            AND lsa.season_type = e.season_type
        '''
def combined_percentile_query(grain):
    rank_cols = SCALED_STATS_RANK_COLS = [f"{s}_scaled" for s in SCALED_STATS]
    rank_exprs = ", ".join(
        f"PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY {c}) AS {c}_percentile"
        for c in rank_cols + CONST_STATS
    )
    return f'''
        WITH combined AS ({combined_player_base(grain)})
        , eligible AS (
            SELECT c.*
            FROM combined c 
            JOIN staging_staging.int_player_eligibility e ON e.player_id = c.player_id
                AND e.season = c.season
                AND e.season_type = c.season_type 
                AND e.league_id = c.league_id 
            WHERE e.meets_min_games_threshold = TRUE
        )
        SELECT player_id, {rank_exprs}
        FROM eligible
        WHERE season = :season
            AND league_id = :league_id
            AND season_type = :season_type
        '''
def combined_leaderboard_query(grain):
    return f'''
        WITH eligible AS (
            {combined_eligible_players(grain)}
        )
        SELECT player_id
            , player_name, current_team_name
            , pts_scaled, reb_scaled, ast_scaled, stl_scaled, blk_scaled, tov_scaled
            , fg3pr, ftr, ts_pct, relative_ts_pct
        FROM eligible 
        WHERE season = :season
            AND league_id = :league_id
            AND season_type = :season_type
        ORDER BY 4 DESC
            '''
@st.cache_resource
def get_engine():
    user = os.environ.get("NBA_DB_USER")
    password = os.environ.get("NBA_DB_PASSWORD")
    host = os.environ.get("NBA_DB_HOST")
    port = os.environ.get("NBA_DB_PORT")
    name = os.environ.get("NBA_DB_NAME")

    sslmode = "disable" if host in ("localhost", "127.0.0.1") else "require"
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}?sslmode={sslmode}")

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