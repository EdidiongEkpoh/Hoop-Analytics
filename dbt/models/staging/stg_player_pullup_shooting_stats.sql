WITH source AS (
    SELECT *
    FROM {{ source('raw_nba', 'player_pullup_shooting_stats') }}
)
SELECT DISTINCT CAST(_extract_season AS VARCHAR) AS season
    , CAST(_extract_league_id AS VARCHAR) AS league_id
    , CAST(_extract_season_type AS VARCHAR) AS season_type
    , CAST("PLAYER_ID" AS VARCHAR) AS player_id
    , CAST("PLAYER_NAME" AS VARCHAR) AS player_name
    , CAST("TEAM_ID" AS VARCHAR) AS team_id
    , CAST("TEAM_ABBREVIATION" AS VARCHAR) AS team_abbreviation
    , CAST("GP" AS INTEGER) AS games_played
    , CAST("MIN" AS INTEGER) AS minutes
    , CAST("PULL_UP_FGM" AS INTEGER) AS pullup_fgm
    , CAST("PULL_UP_FGA" AS INTEGER) AS pullup_fga
    , CAST("PULL_UP_FG_PCT" AS FLOAT) AS pullup_fg_pct
    , CAST("PULL_UP_FG3M" AS INTEGER) AS pullup_fg3m
    , CAST("PULL_UP_FG3A" AS INTEGER) AS pullup_fg3a
    , CAST("PULL_UP_FG3_PCT" AS FLOAT) AS pullup_fg3_pct
    , CAST("PULL_UP_EFG_PCT" AS FLOAT) AS pullup_efg_pct
    , CAST("PULL_UP_PTS" AS INTEGER) AS pullup_pts
FROM source