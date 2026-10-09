{% set stats = ['FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'PLUS_MINUS'] %}
SELECT CAST("TEAM_ID" AS VARCHAR) AS team_id
    , CAST("TEAM_ABBREVIATION" AS VARCHAR) AS team_abbreviation
    , CAST("VS_PLAYER_ID" AS VARCHAR) AS player_id
    , CAST("VS_PLAYER_NAME" AS VARCHAR) AS player_name
    , CAST("COURT_STATUS" AS VARCHAR) AS court_status
    , CAST(_extract_season AS VARCHAR) AS season
    , CAST(_extract_season_type AS VARCHAR) AS season_type
    , CAST(_extract_league_id AS VARCHAR) AS league_id
    , CAST("GP" AS INTEGER) AS games_played
    , CAST("MIN" AS NUMERIC) AS minutes
    {% for s in stats %}
    , CAST("{{ s }}" AS NUMERIC) AS {{ s | lower }}
    {% endfor %}
FROM {{ source('raw_nba', 'team_player_on_off') }}