WITH source AS (
    SELECT *
    FROM {{ source('raw_nba', 'player_catch_shoot_stats') }}
)
SELECT CAST(_extract_season AS VARCHAR) AS season
    , CAST(_extract_league_id AS VARCHAR) AS league_id
    , CAST(_extract_season_type AS VARCHAR) AS season_type
    , CAST("PLAYER_ID" AS VARCHAR) AS player_id
    , CAST("PLAYER_NAME" AS VARCHAR) AS player_name
    , CAST("TEAM_ID" AS VARCHAR) AS team_id
    , CAST("TEAM_ABBREVIATION" AS VARCHAR) AS team_abbreviation
    , CAST("GP" AS INTEGER) AS games_played
    , CAST("MIN" AS INTEGER) AS minutes
    , CAST("CATCH_SHOOT_FGM" AS INTEGER) AS catch_shoot_fgm
    , CAST("CATCH_SHOOT_FGA" AS INTEGER) AS catch_shoot_fga
    , CAST("CATCH_SHOOT_FG_PCT" AS FLOAT) AS catch_shoot_fg_pct
    , CAST("CATCH_SHOOT_FG3M" AS INTEGER) AS catch_shoot_fg3m
    , CAST("CATCH_SHOOT_FG3A" AS INTEGER) AS catch_shoot_fg3a
    , CAST("CATCH_SHOOT_FG3_PCT" AS FLOAT) AS catch_shoot_fg3_pct
    , CAST("CATCH_SHOOT_EFG_PCT" AS FLOAT) AS catch_shoot_efg
    , CAST("CATCH_SHOOT_PTS" AS FLOAT) AS catch_shoot_pts
FROM source