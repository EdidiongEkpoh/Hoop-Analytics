SELECT CAST(_extract_season AS VARCHAR) AS season
    , CAST(_extract_league_id AS VARCHAR) AS league_id
    , CAST(_extract_season_type AS VARCHAR) AS season_type
    , CAST("CLOSE_DEF_PERSON_ID" AS VARCHAR) AS player_id
    , CAST("PLAYER_NAME" AS VARCHAR) AS player_name
    , CAST("PLAYER_LAST_TEAM_ID" AS VARCHAR) AS team_id
    , CAST("PLAYER_LAST_TEAM_ABBREVIATION" AS VARCHAR) AS team_abbreviation
    , CAST("PLAYER_POSITION" AS VARCHAR) AS position
    , CAST(_pull_key AS VARCHAR) AS defense_category
    , CAST("GP" AS INTEGER) AS games_played
    , CAST("D_FGM" AS NUMERIC) AS d_fgm
    , CAST("D_FGA" AS NUMERIC) AS d_fga
    , CAST("D_FG_PCT" AS NUMERIC) AS d_fg_pct
    , CAST("NORMAL_FG_PCT" AS NUMERIC) AS normal_fg_pct
    , CAST("PCT_PLUSMINUS" AS NUMERIC) AS fg_pct_diff
FROM {{ source('raw_nba', 'player_defense_dashboard')}}