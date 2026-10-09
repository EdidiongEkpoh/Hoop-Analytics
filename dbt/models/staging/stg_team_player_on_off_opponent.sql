{% set stats = ['FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS'] %}
SELECT CAST("TEAM_ID" AS VARCHAR) AS team_id
    , CAST("VS_PLAYER_ID" AS VARCHAR) AS player_id
    , CAST("COURT_STATUS" AS VARCHAR) AS court_status
    , CAST(_extract_season AS VARCHAR) AS season
    , CAST(_extract_season_type AS VARCHAR) AS season_type
    , CAST(_extract_league_id AS VARCHAR) AS league_id
    {% for s in stats %}
    , CAST("OPP_{{ s }}" AS NUMERIC) AS opp_{{ s | lower }}
    {% endfor %}
FROM {{ source('raw_nba', 'team_player_on_off_opponent') }}