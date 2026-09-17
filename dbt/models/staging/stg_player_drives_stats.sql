WITH source AS (
    SELECT *
    FROM {{ source('raw_nba', 'player_drives_stats') }}
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
    , CAST("DRIVES" AS INTEGER) AS drives
    , CAST("DRIVE_FGM" AS INTEGER) AS drive_fgm
    , CAST("DRIVE_FGA" AS INTEGER) AS drive_fga
    , CAST("DRIVE_FG_PCT" AS FLOAT) AS drive_fg_pct
    , CAST("DRIVE_FTM" AS INTEGER) AS drive_ftm
    , CAST("DRIVE_FTA" AS INTEGER) AS drive_fta
    , CAST("DRIVE_FT_PCT" AS FLOAT) AS drive_ft_pct
    , CAST("DRIVE_PTS" AS INTEGER) AS drive_pts
    , CAST("DRIVE_AST" AS INTEGER) AS drive_ast
    , CAST("DRIVE_TOV" AS INTEGER) AS drive_tov
    , CAST("DRIVE_PF" AS INTEGER) AS drive_pf
FROM source