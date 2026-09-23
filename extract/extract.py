import time 
import logging
import os 
from dotenv import load_dotenv 
import argparse

from sqlalchemy import create_engine, text, inspect
import json 
from pathlib import Path 

import pandas as pd 
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import leaguegamelog, boxscoreadvancedv3,  commonteamroster, commonplayerinfo, leaguestandingsv3, shotchartdetail, leaguedashptstats, leaguedashplayerstats

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
CHECKPOINT_EVERY_N_GAMES = 100
CHECKPOINT_EVERY_N_PLAYERS = 50

CHECKPOINT_DIR = Path(__file__).parent.parent / 'extract' / 'checkpoints'

SEASON_LEVEL_TABLES = [
    "raw.player_info", "raw.player_basic_boxscores", 
    "raw.team_rosters", "raw.team_basic_boxscores", 
    "raw.standings", "raw.shot_chart_detail", "raw.shot_zone_league_averages",
    "raw.player_catch_shoot_stats", "raw.player_drives_stats", "raw.player_pullup_shooting_stats",
    "raw.player_postup_stats", "raw.player_scoring_breakdown", "raw.player_advanced_boxscores", "raw.team_advanced_boxscores"
]
LEAGUE_TYPE = {"00": "NBA", "10": "WNBA", "20": "G League"}
def fetch_with_retry(fetch_fn, *args, max_retries=MAX_RETRIES, **kwargs):
    for attempt in range(1, max_retries+1):
        try:
            return fetch_fn(*args, **kwargs)
        except Exception as e:
            logging.warning(f"attempt {attempt} failed: {e}.")
            if attempt == max_retries:
                raise 
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)

def get_checkpoint_paths(season, league_id, season_type):
    tag = f"{season}_{league_id}_{season_type.replace(' ', '')}"
    return {
        "processed_games": CHECKPOINT_DIR / f"processed_games_{tag}.json",
        "failed_games": CHECKPOINT_DIR / f"failed_games_{tag}.json",
        "processed_players": CHECKPOINT_DIR / f"processed_players_{tag}.json",
        "failed_players": CHECKPOINT_DIR / f"failed_players_{tag}.json",
        "failed_teams": CHECKPOINT_DIR / f"failed_teams_{tag}.json",
        "failed_shot_teams": CHECKPOINT_DIR / f"failed_shot_teams_{tag}.json"
    }

def clear_season_level(season, league_id, season_type, engine, incremental=False):
    tables_to_clear = SEASON_LEVEL_TABLES
    if incremental:
        skip = ["raw.player_advanced_boxscores", "raw.team_advanced_boxscores"]
        tables_to_clear = [t for t in SEASON_LEVEL_TABLES if t not in skip]
    inspector = inspect(engine)
    tables_to_clear = ['raw.standings']
    with engine.begin() as conn:
        for table_name in tables_to_clear:
            schema, table = table_name.split('.')
            if not inspector.has_table(table, schema=schema):
                logging.info(f"Skipping clear for {table_name}.")
            elif table_name in ["raw.player_info", "raw.team_rosters"]:
                conn.execute(
                    text(f"""
                        DELETE FROM {schema}.{table}
                        WHERE _extract_season = :season
                            AND _extract_league_id = :league
                    """), {"season": season, "league": league_id}
                )
                logging.info(f"Cleared existing rows for {season}/{LEAGUE_TYPE[league_id]} from {table_name}.")
            else:
                conn.execute(
                    text(f"""
                        DELETE FROM {schema}.{table}
                        WHERE _extract_season = :season
                            AND _extract_league_id = :league
                            AND _extract_season_type = :stype
                        """),
                        {"season": season, "league": league_id, "stype": season_type}
                )
                logging.info(f"Cleared existing rows for {season}/{LEAGUE_TYPE[league_id]}/{season_type} from {table_name}.")

    logging.info(f"Finished clearing data for {season}/{LEAGUE_TYPE[league_id]}/{season_type}.")

def load_to_postgres(df, table_name, engine, if_exists="append"):
    schema, table = table_name.split('.')
    if if_exists == "replace":
        inspector = inspect(engine)
        if inspector.has_table(table, schema=schema):
            with engine.begin() as conn:
                conn.execute(text(f'TRUNCATE TABLE {schema}.{table}'))
        df.to_sql(table, schema=schema, con=engine, if_exists="append", index=False)
    else:
        df.to_sql(table, schema=schema, con=engine, if_exists=if_exists, index=False) 

    logging.info(f"Loaded {len(df)} rows into {table_name}.")

def get_bulk_pulls(season, league_id, season_type):
    pulls = [
        
    ]    

    if season_type == "Regular Season":
        pulls.append({
            "name": "team_standings",
            "fetch_fn": lambda: leaguestandingsv3.LeagueStandingsV3(
                league_id=league_id, season=season, season_type=season_type
            ).get_data_frames()[0],
            "table": 'raw.standings'
        })
    return pulls

def get_advanced_boxscores():
    return {
        "name": "advanced_boxscores",
        "fetch_fn": lambda game_id: boxscoreadvancedv3.BoxScoreAdvancedV3(game_id=game_id),
        "player_table": "raw.player_advanced_boxscores",
        "team_table": "raw.team_advanced_boxscores"
    }

def get_player_info():
    return {
        "fetch_fn": lambda player_id, league_id: commonplayerinfo.CommonPlayerInfo(
            league_id_nullable=league_id, player_id=player_id
        ).get_data_frames()[0],
        "table": "raw.player_info"
    }

def get_team_rosters(season, league_id):
    return {
        "fetch_fn": lambda team_id: commonteamroster.CommonTeamRoster(
            team_id=team_id, season=season, league_id_nullable=league_id
        ).get_data_frames()[0],
        "table": "raw.team_rosters"
    }

def get_shot_charts(season, season_type):
    return {
        "fetch_fn": lambda team_id: shotchartdetail.ShotChartDetail(
            team_id=team_id, player_id=0, context_measure_simple='FGA',
            season_nullable=season, season_type_all_star=season_type
        ).get_data_frames(),
        "shots_table": "raw.shot_chart_detail",
        "league_avg_table": "raw.shot_zone_league_averages"
    }

def checkpoint(rows_dict, ids, pull_config, processed_path, failed_path, season, league_id, season_type, engine):
    for key, table in pull_config.items():
        if rows_dict.get(key):
            batch_df = pd.concat(rows_dict[key], ignore_index=True)
            if key == 'player_info':
                batch_df = stamp_run_metadata(batch_df, season, league_id, season_type, key)
            else:
                batch_df = stamp_run_metadata(batch_df, season, league_id, season_type)
            load_to_postgres(batch_df, table, engine)
    with open(processed_path, 'w') as f:
        json.dump(ids['processed'], f)
    with open(failed_path, 'w') as f:
        json.dump(ids['failed'], f)
    logging.info(f"Checkpoint: {len(ids['processed'])} recorded, {len(ids['failed'])} failed.")
    return {k: [] for k in rows_dict}

def game_level_extract(game_ids, season, league_id, season_type, engine, checkpoint_paths, incremental=False):
    games = get_advanced_boxscores()
    
    
    previously_processed = []
    if incremental and checkpoint_paths['processed_games'].exists():
        with open(checkpoint_paths['processed_games']) as f:
            previously_processed = json.load(f)

    game_ids_to_get = [g for g in game_ids if g not in previously_processed]
    logging.info(f"{len(previously_processed)} games have previously been processed; {len(game_ids_to_get)} games still to retrieve.")
    games_dict = {'player_advanced_games': [], 'team_advanced_games': []}
    id_dict = {"processed": list(previously_processed), "failed": []}



    for i, game_id in enumerate(game_ids_to_get):
        try:
            boxscore = fetch_with_retry(games['fetch_fn'], game_id)
            games_dict['player_advanced_games'].append(boxscore.player_stats.get_data_frame())
            games_dict['team_advanced_games'].append(boxscore.team_stats.get_data_frame())
            id_dict['processed'].append(game_id)
        except Exception as e:
            logging.warning(f"Error fetching game_id {game_id}: {e}.")
            if game_id not in id_dict['failed']:
                id_dict['failed'].append(game_id)

        time.sleep(RATE_LIMIT_SLEEP)

        if i % CHECKPOINT_EVERY_N_GAMES == 0 and i > 0:
            games_dict = checkpoint(
                games_dict, id_dict,
                pull_config={'player_advanced_games': games['player_table'],
                             'team_advanced_games': games['team_table']},
                processed_path=checkpoint_paths['processed_games'],
                failed_path=checkpoint_paths['failed_games'],
                season=season, league_id=league_id, season_type=season_type, engine=engine
            )    

    logging.info("Last game checkpoint...")
    checkpoint(
                games_dict, id_dict, 
                pull_config={'player_advanced_games': games['player_table'],
                             'team_advanced_games': games['team_table']},
                processed_path=checkpoint_paths['processed_games'],
                failed_path=checkpoint_paths['failed_games'],
                season=season, league_id=league_id, season_type=season_type, engine=engine
            )    

def team_dimension_extract(season, league_id, season_type, engine):
    roster_pull = get_team_rosters(season, league_id)
    team_ids = [t['id'] for t in teams.get_teams()]
    rosters = []
    failed_teams = []

    for team_id in team_ids:
        try:
            df = fetch_with_retry(roster_pull['fetch_fn'], team_id)
            rosters.append(df)
        except Exception as e:
            logging.warning(f"Failed roster for team {team_id}: {e}.")
            failed_teams.append(team_id)

        time.sleep(RATE_LIMIT_SLEEP)

    if rosters:
        roster_df = pd.concat(rosters, ignore_index=True)
        roster_df = stamp_run_metadata(roster_df, season, league_id, season_type, 'team_rosters')
        load_to_postgres(roster_df, roster_pull['table'], engine)
    if failed_teams:
        paths = get_checkpoint_paths(season, league_id, season_type)
        with open(paths['failed_teams'], 'w') as f:
            json.dump(failed_teams, f)

    logging.info(f"Team dimension extract: {len(rosters)} succeeded, {len(failed_teams)} failed.")

def player_dimension_extract(player_ids, season, league_id, season_type, engine, checkpoint_paths, incremental=False):
    player_info_pull = get_player_info()
    previously_processed = []
    if incremental and checkpoint_paths['processed_players'].exists():
        with open(checkpoint_paths['processed_players']) as f:
            previously_processed = json.load(f)
    
    player_ids_to_get = [p for p in player_ids if p not in previously_processed]
    logging.info(f"{len(previously_processed)} players have previously been processed; {len(player_ids_to_get)} players still to retrieve.")
    info_dict = {'player_info': []}
    id_dict = {'processed': list(previously_processed), 'failed': []}
    for i, player_id in enumerate(player_ids_to_get):
        try:
            df = fetch_with_retry(player_info_pull['fetch_fn'], player_id, league_id)
            info_dict['player_info'].append(df)
            id_dict['processed'].append(player_id.item())
        except Exception as e:
            logging.warning(f"Failed to extract player info for {player_id}: {e}.")
            id_dict['failed'].append(player_id.item())

        time.sleep(RATE_LIMIT_SLEEP)

        if i % CHECKPOINT_EVERY_N_PLAYERS == 0 and i > 0:
            info_dict = checkpoint(
                info_dict, id_dict, 
                pull_config={'player_info': player_info_pull['table']},
                processed_path=checkpoint_paths['processed_players'],
                failed_path=checkpoint_paths['failed_players'],
                season=season, league_id=league_id, season_type=season_type, engine=engine
            )


    logging.info("Last player checkpoint...")
    checkpoint(
        info_dict, id_dict, 
        pull_config={'player_info': player_info_pull['table']},
        processed_path=checkpoint_paths['processed_players'],
        failed_path=checkpoint_paths['failed_players'],
        season=season, league_id=league_id, season_type=season_type, engine=engine
    )

def shot_chart_extract(season, league_id, season_type, engine):
    shot_pull = get_shot_charts(season, season_type)
    team_ids = [t['id'] for t in teams.get_teams()]
    shot_rows = []
    league_avg_df = None
    failed_teams = []

    for team_id in team_ids:
        try:
            dfs = fetch_with_retry(shot_pull['fetch_fn'], team_id)
            shot_rows.append(dfs[0])
            if league_avg_df is None:
                league_avg_df = dfs[1]

        except Exception as e:
            logging.warning(f"Failed shot chart for team {team_id}: {e}.")
            failed_teams.append(team_id)

        time.sleep(RATE_LIMIT_SLEEP)

    if shot_rows:
        shots_df = pd.concat(shot_rows, ignore_index=True)
        shots_df = stamp_run_metadata(shots_df, season, league_id, season_type, 'shot_chart_detail')
        load_to_postgres(shots_df, shot_pull['shots_table'], engine)
    if league_avg_df is not None:
        league_avg_df = stamp_run_metadata(league_avg_df, season, league_id, season_type, 'shot_zone_league_averages')
        load_to_postgres(league_avg_df, shot_pull['league_avg_table'], engine)
    if failed_teams:
        paths = get_checkpoint_paths(season, league_id, season_type)
        with open(paths['failed_shot_teams'], 'w') as f:
            json.dump(failed_teams, f)
    
    logging.info(f"Shot chart extract: {len(shot_rows)} teams succeeded. {len(failed_teams)} failed.")

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




def stamp_run_metadata(df, season, league_id, season_type, pull_name=''):
    '''
    Adds season_id / league_id / season_type columns into the DataFrame before load.
    Required since nba_api endpoints doing return these fields on their own.
    '''
    if pull_name == 'team_standings':
        df = df.loc[:, ~df.columns.str.startswith('Seeding_Game')]
    df = df.copy()
    if pull_name in ['player_info', 'team_rosters']:
        df['_extract_season'] = season
        df['_extract_league_id'] = league_id 
    else:
        df['_extract_season'] = season
        df['_extract_league_id'] = league_id
        df['_extract_season_type'] = season_type 
    return df

def run_extract(season, league_id, season_type, engine, incremental=False):
    logging.info(f"Clearing existing rows for {season}/{LEAGUE_TYPE[league_id]}/{season_type} before reload.")
    clear_season_level(season, league_id, season_type, engine, incremental=incremental)

    checkpoint_paths = get_checkpoint_paths(season, league_id, season_type)

    logging.info(f"{'---' * 10} Season-level extract: {season} / {LEAGUE_TYPE[league_id]} / {season_type} {'---' * 10}")
    season_stats = {}
    for pull in get_bulk_pulls(season, league_id, season_type):
        try:
            logging.info(f"Fetching data for {pull['name']}...")
            df = fetch_with_retry(pull['fetch_fn'])
            if pull.get('static'):
                load_to_postgres(df, pull['table'], engine, if_exists="replace")
            else:
                df = stamp_run_metadata(df, season, league_id, season_type, pull['name'])
                load_to_postgres(df, pull['table'], engine)
            season_stats[pull['name']] = df
        except Exception as e:
            logging.error(f"Error occurred while fetching data for {pull['name']}: {e}")
            season_stats[pull['name']] = None

    #logging.info(f"{'---' * 10} Game-level extract: {season} / {LEAGUE_TYPE[league_id]} / {season_type} {'---' * 10}")
    #if season_stats.get('team_basic_boxscores') is None:
        #raise RuntimeError("team_basic_boxscores failed to load. Therefore cannot derive game_ids for game-level extract.")
    #game_ids = season_stats['team_basic_boxscores']['GAME_ID'].unique()
    #game_level_extract(game_ids, season, league_id, season_type, engine, checkpoint_paths, incremental=incremental)

    #logging.info(f"{'---' * 10} Team dimension extract: {season} / {LEAGUE_TYPE[league_id]} / {season_type} {'---' * 10}")
    #team_dimension_extract(season, league_id, season_type, engine)

    #logging.info(f"{'---' * 10} Player dimension extract: {season} / {LEAGUE_TYPE[league_id]} / {season_type} {'---' * 10}")
    #if season_stats.get('player_basic_boxscores') is None:
        #raise RuntimeError("player_basic_boxscores failed to load. Therefore cannot derive player_ids for player-level extract.")
    #player_ids = season_stats['player_basic_boxscores']['PLAYER_ID'].unique()
    #player_dimension_extract(player_ids, season, league_id, season_type, engine, checkpoint_paths)

    #logging.info(f"{'---' * 10} Shot chart extract: {season} / {LEAGUE_TYPE[league_id]} / {season_type} {'---' * 10}")
    #shot_chart_extract(season, league_id, season_type, engine)

def main():
    args = parse_args()
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"postgresql://{NBA_DB_USER}:{NBA_DB_PASSWORD}@{NBA_DB_HOST}:{NBA_DB_PORT}/{NBA_DB_NAME}")

    start_script = time.time()

    for season in args.seasons:
        start_season = time.time()
        logging.info(f"{'==' * 10} Starting extract: season={season}, league={args.league}, season_type={args.season_type} {'==' * 10}")
        try:
            run_extract(season, args.league, args.season_type, engine, args.incremental)
        except Exception as e:
            logging.error(f"Season {season} failed entirely: {e}.")
        logging.info(f"{'====' * 10} Finished {season} in {((time.time() - start_season) / 60):.2f} minutes {'====' * 10}")
    elapsed = time.time() - start_script
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = int(elapsed % 60)
    logging.info(f"Extract complete. {hours} hours, {minutes} minutes, and {seconds} seconds elapsed.")

if __name__ == "__main__":
    main()