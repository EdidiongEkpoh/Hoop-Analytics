from lib import db
from lib.db import LEAGUE_ID, table 
import pandas as pd

TRACKING_TABLES = {
    "per_game": "fct_player_tracking_stats_per_game",
    "per_36": "fct_player_tracking_stats_per_36",
    "per_75": "fct_player_tracking_stats_per_75",
    "per_100": "fct_player_tracking_stats_per_100"
}
def seasons():
    df = db.query_live(
        f"SELECT DISTINCT season FROM {table(f'fct_league_season')}"
        " WHERE league_id = :league_id ORDER BY season DESC",
        {"league_id": LEAGUE_ID}
    )
    return df['season'].tolist()

def current_season():
    all_seasons = seasons()
    return all_seasons[0] if all_seasons else None

def season_types(season):
    df = db.query_live(
        f"SELECT DISTINCT season_type FROM {table('fct_league_season')}"
        " WHERE season = :season AND league_id = :league_id",
        {"season": season, "league_id": LEAGUE_ID}
    )
    order = {"Regular Season": 0, "Playoffs": 1}
    return sorted(df["season_type"].tolist(), key=lambda t: order.get(t, 9))

def _query(sql, params, season=None):
    params = {"league_id": LEAGUE_ID, **params}
    if season is not None and season != current_season():
        return db.query_static(sql, params)
    return db.query_live(sql, params)

def data_through():
    df = db.query_live(f"SELECT MAX(game_date) AS d FROM {table('fct_team_games')}")
    return None if df.empty or pd.isna(df['d'].iloc[0]) else str(df['d'].iloc[0])[:10]
def league_seasons(season_type):
    return _query(
        f'''
        SELECT *
        FROM {table('fct_league_season')}
        WHERE league_id = :league_id
            AND season_type = :season_type
        ORDER BY season
        '''
        , {"season_type": season_type}
    )

def team_seasons(season_type): 
    return _query(
        f'''
        SELECT *
        FROM {table('fct_team_season')}
        WHERE league_id = :league_id
            AND season_type = :season_type
        '''
        , {"season_type": season_type}
    )

def standings(season):
    return _query(
        f'''
        SELECT *
        FROM {table('dim_standings')}
        WHERE league_id = :league_id
            AND season = :season
        ORDER BY win_pct DESC
        '''
        , {"season": season}
        , season
    )
def team_games(team_id, season, season_type):
    return _query(
        f'''
        SELECT *
        FROM {table('fct_team_games')}
        WHERE team_id = :team_id
            AND season = :season
            AND league_id = :league_id
        ORDER BY game_date
        '''
        , {"team_id": str(team_id), "season": season, "season_type": season_type},
        season
    )

def team_play_types(season, season_type):
    return _query(
        f'''
        SELECT *
        FROM {table('fct_team_play_types')}
        WHERE season = :season
            AND league_id = :league_id
            AND season_type = :season_type
        '''
        , {'season': season, "season_type": season_type}
        , season
    )

def roster(team_id, season):
    return _query(
        f'''
        SELECT *
        FROM {table('dim_team_rosters')}    
        WHERE team_id = :team_id
            AND season = :season
            AND league_id = :league_id
        '''
        , {"team_id": str(team_id), "season": season}
        , season
    )

def player_seasons(season_type):
    '''
    Player season stats for every available season across teams.
    '''
    return _query(
        f'''
        SELECT *
        FROM {table('fct_player_season')}
        WHERE league_id = :league_id
            AND season_type = :season_type
        '''
        , {"season_type": season_type}
    )

def player_seasons_by_team(season, season_type):
    '''
    Player season stats separated by team
    '''
    return _query(
        f'''   
        SELECT *
        FROM {table('fct_player_season_by_team')}
        WHERE season = :season
            AND league_id = :league_id
            AND season_type = :season_type
        '''
        , {"season": season, "season_type": season_type}
        , season
    )

def player_bio(player_id):
    df = _query(f'''
        SELECT *
        FROM {table('dim_players')}
        WHERE player_id = :player_id
        '''
        , {"player_id": str(player_id)}
    )
    return df.iloc[0] if not df.empty else None

def player_games(player_id, season, season_type):
    return _query(
        f'''
        SELECT *
        FROM {table('fct_player_games')}
        WHERE player_id = :player_id
            AND season = :season
            AND league_id = :league_id
            AND season_type = :season_type
        ORDER BY game_date
        '''
        , {"player_id": str(player_id), "season": season, "season_type": season_type}
        , season
    )

def player_play_types(season, season_type):
    return _query(
        f'''
        SELECT *
        FROM {table('fct_player_play_types')}
        WHERE season = :season
            AND league_id = :league_id
            AND season_type = :season_type
        '''
        , {"season": season, "season_type": season_type}
        , season
    )
        
def player_on_off(season, season_type):
    return _query(
        f'''
        SELECT *
        FROM {table('fct_player_on_off')}
        WHERE season = :season
            AND league_id = :league_id
            AND season_type = :season_type
        '''
        , {"season": season, "season_type": season_type}
        , season
    )

def player_defense(season_type):
    return _query(
        f'''
        SELECT *
        FROM {table('fct_player_defense')}
        WHERE league_id = :league_id
            AND season_type = :season_type
        '''
        , {"season_type": season_type}
    )

def player_tracking(season, season_type, grain):
    '''
    Tracking stats at chosen grain along with season percentages
    '''
    scaled = TRACKING_TABLES[grain]
    return _query(
        f'''
        SELECT s.*
            , t.catch_shoot_fg_pct, t.catch_shoot_fg3_pct, t.catch_shoot_efg
            , t.pullup_fg_pct, t.pullup_fg3_pct, t.pullup_efg_pct
            , t.drive_fg_pct, t.post_touch_fg_pct
            , t.pct_pts_paint, t.pct_ast_fgm, t.pct_uast_fgm
            , t.pct_ast_2pm, t.pct_uast_2pm, t.pct_ast_3pm, t.pct_uast_3pm
        FROM {table(scaled)} s
        JOIN {table('fct_player_tracking_stats')} t ON t.player_id = s.player_id
            AND t.season = s.season
            AND t.league_id = s.league_id
            AND t.season_type = s.season_type
        WHERE s.season = :season
            AND s.league_id = :league_id
            AND s.season_type = :season_type
        '''
        , {"season": season, "season_type": season_type}
        , season
    )


def shots(season, season_type, player_id = None, team_id = None):
    '''
    Shot data for one player or team
    '''
    if (player_id is None) == (team_id is None):
        raise ValueError("Pass exactly one of player_id or team_id")
    column, value = ('player_id', player_id) if player_id is not None else ('team_id', team_id)
    return _query(
        f'''
        SELECT *
        FROM {table('fct_shots')}
        WHERE {column} = :id
            AND season = :season
            AND league_id = :league_id
            AND season_type = :season_type
        '''
        , {"id": str(value), "season": season, "season_type": season_type}
        , season
    )

def shot_zones(season, season_type, player_id = None, team_id = None):
    if (player_id is None) == (team_id is None):
            raise ValueError("Pass exactly one of player_id or team_id")
    column, value = ('player_id', player_id) if player_id is not None else ('team_id', team_id)
    return _query(
        f'''
        SELECT shot_zone_basic
            , shot_zone_area
            , shot_zone_range
            , SUM(fga) AS fga
            , SUM(fgm) AS fgm
            , SUM(fgm)::NUMERIC / NULLIF(SUM(fga), 0) AS fg_pct
            , MAX(league_avg_fg_pct) AS league_avg_fg_pct
            , SUM(fgm)::NUMERIC / NULLIF(SUM(fga), 0) - MAX(league_avg_fg_pct) AS fg_pct_vs_league
        FROM {table('fct_shot_zone_summary')}
        WHERE {column} = :id
            AND season = :season
            AND league_id = :league_id
            AND season_type = :season_type
        GROUP BY 1, 2, 3
        '''
        , {"id": str(value), "season": season, "season_type":season_type}
        , season
    )