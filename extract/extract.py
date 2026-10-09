import time 
import logging
import os 
from dotenv import load_dotenv 
import argparse
import random
import sys

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import URL
import json 
from pathlib import Path 

import pandas as pd 
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import (
    leaguegamelog, 
    boxscoreadvancedv3,  
    commonteamroster, 
    commonplayerinfo, 
    leaguestandingsv3, 
    shotchartdetail, 
    leaguedashptstats, 
    leaguedashplayerstats,
    leaguedashptdefend,
    leaguedashteamstats,
    leaguehustlestatsplayer,
    synergyplaytypes,
    teamplayeronoffdetails
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

load_dotenv()
NBA_DB_USER = os.environ.get('NBA_DB_USER')
NBA_DB_PASSWORD = os.environ.get('NBA_DB_PASSWORD')
NBA_DB_NAME = os.environ.get('NBA_DB_NAME')
NBA_DB_HOST = os.environ.get('NBA_DB_HOST')
NBA_DB_PORT = os.environ.get('NBA_DB_PORT')

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2
RATE_LIMIT_SLEEP = 1.0
API_TIMEOUT = 60
GAMES_PER_BATCH = 100
PLAYERS_PER_BATCH = 50

FAILURE_DIR = Path(__file__).parent.parent / 'extract' / 'failures'

PLAYER_ADV_TABLE = 'raw.player_advanced_boxscores'
TEAM_ADV_TABLE = 'raw.team_advanced_boxscores'
PLAYER_INFO_TABLE = 'raw.player_info'
ROSTER_TABLE = 'raw.team_rosters'
SHOTS_TABLE = 'raw.shot_chart_detail'
SHOT_LEAGUE_AVG_TABLE = 'raw.shot_zone_league_averages'

GAME_ID_COL = "gameId"
PLAYER_INFO_ID_COL = "PERSON_ID"
ROSTER_TEAM_COL = "TeamID"
SHOT_TEAM_COL = "TEAM_ID"

OMIT_SEASON_TYPE = ["player_info", "team_rosters"]

STANDINGS_BUBBLE_COLS = ["ReturnToPlay_East_PI_Flag", "ReturnToPlay_West_PI_Flag", "ReturnToPlay_Already_Eliminated"]

PULL_KEY_COL = "_pull_key"

PLAY_TYPES = [
    'Transition', 'Isolation', 'PRBallHandler', 'PRRollman', 'Postup', 'Spotup', 'Handoff', 'Cut', 'OffScreen', 'OffRebound', 'Misc'
]
PLAY_TYPE_GROUPINGS = ['offensive', 'defensive']

DEFENSE_CATEGORIES = [
    'Overall', '3 Pointers', '2 Pointers', 'Less Than 6Ft', 'Less Than 10Ft', 'Greater Than 15Ft'
]
PT_DEFEND_ID_COLS = [
    "CLOSE_DEF_PERSON_ID", "PLAYER_NAME", "PLAYER_LAST_TEAM_ID", "PLAYER_LAST_TEAM_ABBREVIATION", "PLAYER_POSITION", "AGE", 
    "GP", "G", "FREQ"
]
PT_DEFEND_STAT_COLS = [
    "D_FGM", "D_FGA", "D_FG_PCT", "NORMAL_FG_PCT", "PCT_PLUSMINUS"
]

ON_OFF_PULLS = {
    "Base": ('team_player_on_off', 'raw.team_player_on_off'),
    "Opponent": ("team_play er_on_off_opponent", 'raw.team_player_on_off_opponent')
}
LEAGUE_TYPE = {"00": "NBA", "10": "WNBA", "20": "G League"}


def fetch_with_retry(fetch_fn, *args, max_retries=MAX_RETRIES, **kwargs):
    for attempt in range(1, max_retries+1):
        try:
            return fetch_fn(*args, **kwargs)
        except Exception as e:
            logging.warning(f"Attempt {attempt}/{max_retries} failed: {e}.")
            if attempt == max_retries:
                raise 
            time.sleep(RETRY_BACKOFF_SECONDS * 2 ** (attempt-1) + random.uniform(0, 1))

def native(values):
    return [v.item() if hasattr(v, "item") else v for v in values]

def stamp_run_metadata(df, season, league_id, season_type, pull_name=""):
    '''
    Adds _extract_* columns
    '''
    df = df.copy()
    if pull_name == 'team_standings':
        df = df.loc[:, ~df.columns.str.startswith('Seeding_Game')]

    df['_extract_season'] = season
    df['_extract_league_id'] = league_id
    if pull_name not in OMIT_SEASON_TYPE:
        df['_extract_season_type'] = season_type 

    return df
def scope_for(season, league_id, season_type, pull_name=""):
    scope = {"_extract_season": season, "_extract_league_id": league_id}
    if pull_name not in OMIT_SEASON_TYPE:
        scope['_extract_season_type'] = season_type
    return scope

def where_clause(scope):
    return " AND ".join(f'"{col}" = :{col}' for col in scope)

def replace_rows(conn, df, table_name, scope, key_col=None, keys=None):
    '''
    Deletes the slice of given table matching the scope, then inserts df.
    '''
    schema, table = table_name.split('.')
    deleted = 0
    if inspect(conn).has_table(table, schema=schema):
        where = where_clause(scope)
        params = dict(scope)
        if key_col is not None:
            where += f' AND "{key_col}" = ANY(:keys)'
            params["keys"] = native(keys)
        deleted = conn.execute(text(f"DELETE FROM {table_name} WHERE {where}"), params).rowcount
    if not df.empty:
        df.to_sql(table, schema=schema, con=conn, if_exists="append", index=False)
    logger.info(f"{table_name}: replaced {deleted} rows with {len(df)}.")

def loaded_keys(engine, table_name, key_col, scope):
    '''
    Distinct key values that are already present in this run's slice of table name.
    '''
    schema, table = table_name.split(".")
    if not inspect(engine).has_table(table, schema=schema):
        return set()

    sql = f'SELECT DISTINCT "key{key_col}" FROM {table_name} WHERE {where_clause(scope)}'
    with engine.connect() as conn:
        return {row[0] for row in conn.execute(text(sql), scope)}

def write_failures(kind, ids, season, league_id, season_type):
    tag = f"{season}_{league_id}_{season_type.replace(' ', '')}"
    path = FAILURE_DIR / f"failed_{kind}_{tag}.json"
    if ids:
        path.write_text(json.dumps(native(ids)))
    elif path.exists():
        path.unlink()

def load_static_tables(engine):
    '''
    Loads raw.players and raw.teams
    '''
    for fetch, table_name in [(players.get_players, 'raw.players'), (teams.get_teams, 'raw.teams')]:
        df = pd.DataFrame(fetch())
        schema, table = table_name.split(".")
        with engine.begin() as conn:
            if inspect(conn).has_table(table, schema=schema):
                conn.execute(text(f"TRUNCATE TABLE {table_name}"))
            df.to_sql(table, schema=schema, con=conn, if_exists="append", index=False)
        logger.info(f"{table_name}: loaded {len(df)} rows.")

def get_bulk_pulls(season, league_id, season_type):
    def game_log(kind):
        return lambda: leaguegamelog.LeagueGameLog(
            season=season, league_id=league_id, season_type_all_star=season_type,
            player_or_team_abbreviation=kind, timeout=API_TIMEOUT
        ).get_data_frames()[0]

    def tracking(measure):
        return lambda: leaguedashptstats.LeagueDashPtStats(
            league_id_nullable=league_id, season=season, season_type_all_star=season_type,
            pt_measure_type=measure, player_or_team="Player", timeout=API_TIMEOUT
        ).get_data_frames()[0]

    pulls = [
        {"name": "player_basic_boxscores", "fetch_fn": game_log("P"), "table": "raw.player_basic_boxscores"},
        {"name": "team_basic_boxscores", "fetch_fn": game_log("T"), "table": "raw.team_basic_boxscores"},
        {"name": "catch_shoot_stats", "fetch_fn": tracking("CatchShoot"), "table": "raw.player_catch_shoot_stats"},
        {"name": "drives_stats", "fetch_fn": tracking("Drives"), "table": "raw.player_drives_stats"},
        {"name": "pullup_shooting_stats", "fetch_fn": tracking("PullUpShot"), "table": "raw.player_pullup_shooting_stats"},
        {"name": "postup_stats", "fetch_fn": tracking("PostTouch"), "table": "raw.player_postup_stats"},
        {
            "name": "scoring_breakdown",
            "fetch_fn": lambda: leaguedashplayerstats.LeagueDashPlayerStats(
                league_id_nullable=league_id, season=season, season_type_all_star=season_type,
                measure_type_detailed_defense="Scoring", timeout=API_TIMEOUT
            ).get_data_frames()[0],
            "table": "raw.player_scoring_breakdown"
        },
        {
            "name": "player_hustle_stats",
            "fetch_fn": lambda: leaguehustlestatsplayer.LeagueHustleStatsPlayer(
                league_id_nullable=league_id, season=season, season_type_all_star=season_type, timeout=API_TIMEOUT,
                per_mode_time="Totals"
            ).get_data_frames()[0],
            "table": "raw.player_hustle_stats"
        },
        {
            "name": "team_misc_stats",
            "fetch_fn": lambda: leaguedashteamstats.LeagueDashTeamStats(
                league_id_nullable=league_id, season=season, season_type_all_star=season_type, 
                measure_type_detailed_defense="Misc", per_mode_detailed="Totals",timeout=API_TIMEOUT
            ).get_data_frames()[0],
            "table": "raw.team_misc_stats"
        }
    ]

    if season_type == "Regular Season":
        pulls.append({
            "name": "team_standings",
            "fetch_fn": lambda: leaguestandingsv3.LeagueStandingsV3(
                league_id=league_id, season=season, season_type=season_type, timeout=API_TIMEOUT
            ).get_data_frames()[0].drop(columns=STANDINGS_BUBBLE_COLS, errors="ignore"),
            "table": "raw.standings"
        })
    return pulls

def run_bulk_pulls(season, league_id, season_type, engine):
    results, problems = {}, []
    for pull in get_bulk_pulls(season, league_id, season_type):
        name, table_name = pull['name'], pull['table']
        results[name] = None
        logger.info(f"Fetching {name}...")
        try:
            df = fetch_with_retry(pull['fetch_fn'])
        except Exception as e:
            logger.error(f"{name}: fetch failed, existing rows in {table_name} left untouched. {e}")
            problems.append(f"bulk pull {name} (fetch)")
            continue
        df = stamp_run_metadata(df, season, league_id, season_type, name)
        try:
            with engine.begin() as conn:
                replace_rows(conn, df, table_name, scope_for(season, league_id, season_type, name))
        except Exception as e:
            logger.error(f"{name}: Load failed and was rolled back. {e}")
            problems.append(f"bulk pull {name} (load)")
            continue 
        results[name] = df 

    return results, problems 

def game_level_extract(game_ids, season, league_id, season_type, engine, incremental=False):
    scope = scope_for(season, league_id, season_type)

    if incremental:
        done = (loaded_keys(engine, PLAYER_ADV_TABLE, GAME_ID_COL, scope) & 
                loaded_keys(engine, TEAM_ADV_TABLE, GAME_ID_COL, scope))
        to_get = [g for g in game_ids if g not in done]
        logger.info(f"{len(done)} games already loaded; {len(to_get)} to fetch.")
    else:
        to_get = list(game_ids)
        logger.info(f"Full refresh: fetching {len(to_get)} games.")

    batch = {'ids': [], 'player': [], 'team': []}
    failed = []

    def flush():
        if not batch['ids']:
            return
        player_df = stamp_run_metadata(pd.concat(batch['player'], ignore_index=True), season, league_id, season_type)
        team_df = stamp_run_metadata(pd.concat(batch['team'], ignore_index=True), season, league_id, season_type)

        with engine.begin() as conn:
            replace_rows(conn, player_df, PLAYER_ADV_TABLE, scope, GAME_ID_COL, batch['ids'])
            replace_rows(conn, team_df, TEAM_ADV_TABLE, scope, GAME_ID_COL, batch['ids'])
 
        logger.info(f"{len(batch['ids'])} games loaded.")
        for items in batch.values():
            items.clear()

    for game_id in to_get:
        try:
            box = fetch_with_retry(boxscoreadvancedv3.BoxScoreAdvancedV3, game_id=game_id, timeout=API_TIMEOUT)
            player_df = box.player_stats.get_data_frame()
            team_df = box.team_stats.get_data_frame()
        except Exception as e:
            logger.warning(f"Game {game_id} failed: {e}")
            failed.append(game_id)
        else:
            batch['ids'].append(game_id)
            batch['player'].append(player_df)
            batch['team'].append(team_df)
        time.sleep(RATE_LIMIT_SLEEP)

        if len(batch['ids']) >= GAMES_PER_BATCH:
            flush()
    flush()

    write_failures('games', failed, season, league_id, season_type)
    logger.info(f"Game-level extract: {len(to_get) - len(failed)} succeeded, {len(failed)} failed.")
    return [f'{len(failed)} games failed'] if failed else []


def team_dimension_extract(team_ids, season, league_id, season_type, engine):
    dfs, succeeded, failed = [], [], []
    for team_id in team_ids:
        try:
            df = fetch_with_retry(
                commonteamroster.CommonTeamRoster,
                team_id=team_id, season=season, league_id_nullable=league_id, timeout=API_TIMEOUT
            ).get_data_frames()[0]
            dfs.append(df)
            succeeded.append(team_id)
        except Exception as e:
            logger.warning(f"Roster for team {team_id} failed: {e}.")
            failed.append(team_id)
        time.sleep(RATE_LIMIT_SLEEP)
    
    if succeeded:
        roster_df = stamp_run_metadata(pd.concat(dfs, ignore_index=True), season, league_id, season_type, 'team_rosters')
        with engine.begin() as conn:
            replace_rows(conn, roster_df, ROSTER_TABLE, scope_for(season, league_id, season_type, "team_rosters"), ROSTER_TEAM_COL, succeeded)

    write_failures("teams", failed, season, league_id, season_type)
    logger.info(f"Team dimension extract: {len(succeeded)} succeeded, {len(failed)} failed.")
    return [f"{len(failed)} rosters failed"] if failed else []

def player_dimension_extract(player_ids, season, league_id, season_type, engine):
    '''
    Refreshes player_info for the players in this run's game log.
    '''
    scope = scope_for(season, league_id, season_type, "player_info")
    batch_ids, dfs, failed = [], [], []

    def flush():
        if not batch_ids:
            return
        df = stamp_run_metadata(pd.concat(dfs, ignore_index=True), season, league_id, season_type, 'player_info')
        with engine.begin() as conn:
            replace_rows(conn, df, PLAYER_INFO_TABLE, scope, PLAYER_INFO_ID_COL, batch_ids)
        batch_ids.clear()
        dfs.clear()

    for player_id in player_ids:
        try:
            df = fetch_with_retry(
                commonplayerinfo.CommonPlayerInfo,
                player_id=player_id,league_id_nullable=league_id, timeout=API_TIMEOUT
            ).get_data_frames()[0]
            dfs.append(df)
            batch_ids.append(player_id)
        except Exception as e:
            logger.warning(f"Player info for {player_id} failed: {e}")
            failed.append(player_id)
        time.sleep(RATE_LIMIT_SLEEP)
        if len(batch_ids) >= PLAYERS_PER_BATCH:
            flush()
    flush()

    write_failures("players", failed, season, league_id, season_type)
    logger.info(f"Player dimension extract: {len(player_ids) - len(failed)} succeeed, {len(failed)} failed.")
    return [f"{len(failed)} players failed"] if failed else []


def shot_chart_extract(team_ids, season, league_id, season_type, engine):
    dfs, succeeded, failed = [], [], []
    league_avg_df = None
    for team_id in team_ids:
        try:
            shot_dfs = fetch_with_retry(
                shotchartdetail.ShotChartDetail,
                team_id=team_id, player_id=0, context_measure_simple='FGA', league_id=league_id,
                season_nullable=season, season_type_all_star=season_type, timeout=API_TIMEOUT
            ).get_data_frames()
            dfs.append(shot_dfs[0])
            succeeded.append(team_id)
            if league_avg_df is None:
                league_avg_df = shot_dfs[1]
        except Exception as e:
            logger.warning(f"Shot chart for team {team_id} failed: {e}")
            failed.append(team_id)
        time.sleep(RATE_LIMIT_SLEEP)
    
    scope = scope_for(season, league_id, season_type)
    with engine.begin() as conn:
        if succeeded:
            shots_df = stamp_run_metadata(pd.concat(dfs, ignore_index=True), season, league_id, season_type)
            replace_rows(conn, shots_df, SHOTS_TABLE, scope, SHOT_TEAM_COL, succeeded)
        if league_avg_df is not None:
            league_avg_df = stamp_run_metadata(league_avg_df, season, league_id, season_type)
            replace_rows(conn, league_avg_df, SHOT_LEAGUE_AVG_TABLE, scope)
    
    write_failures("shot_teams", failed, season, league_id, season_type)
    logger.info(f"Shot chart extract: {len(succeeded)} succeeded, {len(failed)} failed.")
    return [f"{len(failed)} shot charts failed"] if failed else []

def run_keyed_pull(name, table_name, calls, season, league_id, season_type, engine):
    '''
    Runs several API calls into one raw table. calls is a list of (key, fetch_fn).
    Each call's rows are tagged with its key in _pull_key and replaced with their own.
    '''
    dfs, succeeded, failed = [], [], []
    for key, fetch_fn in calls:
        try:
            df = fetch_with_retry(fetch_fn)
        except Exception as e:
            logger.warning(f"{name} [{key}] failed: {e}")
            failed.append(key)
        else:
            dfs.append(df.assign(**{PULL_KEY_COL: key}))
            succeeded.append(key)
        time.sleep(RATE_LIMIT_SLEEP)
    
    problems = []
    if succeeded:
        df = stamp_run_metadata(pd.concat(dfs, ignore_index=True), season, league_id, season_type, name)
        try:
            with engine.begin() as conn:
                replace_rows(conn, df, table_name, scope_for(season, league_id, season_type, name), PULL_KEY_COL, succeeded)
        except Exception as e:
            logger.error(f"{name}: Load failed and was rolled back. {e}")
            problems.append(f"{name} (load)")
    
    write_failures(name, failed, season, league_id, season_type)
    logger.info(f"{name}: {len(succeeded)} succeeded, {len(failed)} failed.")
    if failed:
        problems.append(f"{name}: {len(failed)} of {len(calls)} failed.")
    return problems

def play_type_extract(season, league_id, season_type, engine):
    '''
    Synergy play types for players and teams for offense and defense.
    '''
    problems = []
    for abbreviation, name, table_name in [
        ('P', 'player_play_types', 'raw.player_play_types'),
        ('T', 'team_play_types', 'raw.team_play_types')
    ]:
        calls = [
            (
            f"{play_type}|{grouping}",
            lambda pt=play_type, g=grouping, a=abbreviation: synergyplaytypes.SynergyPlayTypes(
                league_id=league_id, season=season, season_type_all_star=season_type,
                player_or_team_abbreviation=a, per_mode_simple="Totals", play_type_nullable=pt, type_grouping_nullable=g, timeout=API_TIMEOUT
            ).get_data_frames()[0]
            )
            for play_type in PLAY_TYPES
            for grouping in PLAY_TYPE_GROUPINGS
        ]
        problems += run_keyed_pull(name, table_name, calls, season, league_id, season_type, engine)
    return problems

def normalize_pt_defend(df, category):
    '''
    Renames a LeagueDashPtDefend category's stat columns to the inputted name.
    '''
    expected_width = len(PT_DEFEND_ID_COLS) + len(PT_DEFEND_STAT_COLS)
    if list(df.columns[:len(PT_DEFEND_ID_COLS)]) != PT_DEFEND_ID_COLS or len(df.columns) != expected_width:
        raise ValueError(f"Unexpected LeagueDashPtDefend columns for '{category}': {list(df.columns)}")
    df = df.copy()
    df.columns = PT_DEFEND_ID_COLS + PT_DEFEND_STAT_COLS
    return df

def defense_dashboard_extract(season, league_id, season_type, engine):
    '''
    Opponent shooting with each player as the closest defender, overall, and by shot distance.
    '''
    calls = [
        (
            category,
            lambda c=category: normalize_pt_defend(
                leaguedashptdefend.LeagueDashPtDefend(
                    league_id=league_id, season=season, season_type_all_star=season_type,
                    defense_category=c, per_mode_simple="Totals", timeout=API_TIMEOUT
                ).get_data_frames()[0],
                c
            )
        )
        for category in DEFENSE_CATEGORIES
    ]
    return run_keyed_pull("player_defense_dashboard", "raw.player_defense_dashboard", calls, season, league_id, season_type, engine)

def fetch_on_off(team_id, measure, season, league_id, season_type):
    endpoint = teamplayeronoffdetails.TeamPlayerOnOffDetails(
        team_id=team_id, season=season, season_type_all_star=season_type, league_id_nullable=league_id,
        measure_type_detailed_defense=measure, per_mode_detailed="Totals", timeout=API_TIMEOUT
    )

    on_off = pd.concat([
        endpoint.players_off_court_team_player_on_off_details.get_data_frame(),
        endpoint.players_on_court_team_player_on_off_details.get_data_frame()
    ], ignore_index=True)

    if "COURT_STATUS" not in on_off.columns:
        raise ValueError(f"TeamPlayerOnOffDetails ({measure}) returned no COURT_STATUS column")
    return on_off

def on_off_extract(team_ids, season, league_id, season_type, engine):
    '''
    Team and opponent box scopre with each player's on and offs.
    '''
    problems = []
    for measure, (name, table_name) in ON_OFF_PULLS.items():
        calls = [
            (str(team_id), lambda t=team_id, m=measure: fetch_on_off(t, m, season, league_id, season_type))
            for team_id in team_ids
        ]
        problems += run_keyed_pull(name, table_name, calls, season, league_id, season_type, engine)
    return problems

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
        query={"sslmode": os.environ.get("NBA_DB_SSLMODE", "prefer")}
    )
    return create_engine(url, pool_pre_ping=True)

def parse_args():
    parser = argparse.ArgumentParser(description="Extract NBA stats and load into the warehouse.")
    parser.add_argument(
        '--seasons', nargs="+", default=['2025-26'], 
        help="One or more seasons, e.g. '--seasons 2024-25 2025-26'."
    )
    parser.add_argument(
        '--league', default="00", choices=["00", "10", "20"],
        help="League ID: 00=NBA, 10=WNBA, 20=G League"
    )
    parser.add_argument(
        "--season-type", default="Regular Season", choices=["Regular Season", "Playoffs"],
        help="Season type to pull. NOTE: Standings extract is skipped for the Playoffs."
        "Playoff standings isn't a meaningful concept the way regular season standings are."
    )
    parser.add_argument(
        '--incremental', action="store_true", help='Skip games already recorded in processed_games.json. Used for daily in-season runs.'
    )
    return parser.parse_args()


def run_extract(season, league_id, season_type, engine, incremental=False):
    '''
    Returns a list of problems if run not sucessful.
    '''
    label = f"{season} / {LEAGUE_TYPE[league_id]} / {season_type}"
    banner = "---" * 10

    logger.info(f"{banner} Season-level extract: {label} {banner}")
    bulk, problems = run_bulk_pulls(season, league_id, season_type, engine)

    team_log = bulk.get("team_basic_boxscores")
    if team_log is None:
        problems.append("Skipped game, roster and shot extracts: no game log.")
        return problems

    game_ids = team_log['GAME_ID'].unique().tolist()
    team_ids = native(team_log['TEAM_ID'].unique())

    logger.info(f"{banner} Game-level extract: {label} {banner}")
    problems += game_level_extract(game_ids, season, league_id, season_type, engine, incremental)

    logger.info(f"{banner} Team dimesnion extract: {label} {banner}")
    problems += team_dimension_extract(team_ids, season, league_id, season_type, engine)

    logger.info(f"{banner} Player dimension extract: {label} {banner}")
    player_log = bulk.get("player_basic_boxscores")
    if player_log is None:
        problems.append("Skipped player dimension extract: No player game log.")
    else:
        player_ids = native(player_log['PLAYER_ID'].unique())
        problems += player_dimension_extract(player_ids, season, league_id, season_type, engine)

    logger.info(f"{banner} Shot chart extract: {label} {banner}")
    problems += shot_chart_extract(team_ids, season, league_id, season_type, engine)

    logger.info(f"{banner} Play types: {label} {banner}")
    problems += play_type_extract(season, league_id, season_type, engine)

    logger.info(f"{banner} Defense dashboard: {label} {banner}")
    problems += defense_dashboard_extract(season, league_id, season_type, engine)

    logger.info(f"{banner} On/Off: {label} {banner}")
    problems += on_off_extract(team_ids, season, league_id, season_type, engine)

    return problems

def main():
    args = parse_args()
    FAILURE_DIR.mkdir(parents=True, exist_ok=True)
    engine = get_engine()
    start = time.time()

    load_static_tables(engine)

    all_problems = {}
    for season in args.seasons:
        start_season = time.time()
        logging.info(f"{'==' * 10} Starting extract: season={season}, league={args.league}, season_type={args.season_type} {'==' * 10}")
        try:
            problems = run_extract(season, args.league, args.season_type, engine, args.incremental)
        except Exception as e:
            logging.error(f"Season {season} crashed: {e}.")
            problems = [f"crashed: {e}"]
        if problems:
            all_problems[season] = problems
        logging.info(f"{'====' * 10} Finished {season} in {((time.time() - start_season) / 60):.2f} minutes. {'====' * 10}")

    elapsed = int(time.time()) - start
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = int(elapsed % 60)
    logging.info(f"Extract complete. {hours} hours, {minutes} minutes, and {seconds} seconds elapsed.")

    if all_problems:
        for season, problems in all_problems.items():
            logger.error(f"{season}: " + ": ".join(problems))
        sys.exit(1)
    

if __name__ == "__main__":
    main()