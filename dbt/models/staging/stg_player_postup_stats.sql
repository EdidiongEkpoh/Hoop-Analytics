WITH source AS (
    SELECT *
    FROM {{ source('raw_nba', 'player_postup_stats') }}
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
    , CAST("TOUCHES" AS INTEGER) AS touches
    , CAST("POST_TOUCHES" AS INTEGER) AS post_touches
    , CAST("POST_TOUCH_FGM" AS INTEGER) AS post_touch_fgm
    , CAST("POST_TOUCH_FGA" AS INTEGER) AS post_touch_fga
    , CAST("POST_TOUCH_FG_PCT" AS FLOAT) AS post_touch_fg_pct
    , CAST("POST_TOUCH_FTM" AS INTEGER) AS post_touch_ftm
    , CAST("POST_TOUCH_FTA" AS INTEGER) AS post_touch_fta
    , CAST("POST_TOUCH_FT_PCT" AS FLOAT) AS post_touch_ft_pct
    , CAST("POST_TOUCH_PTS" AS INTEGER) AS post_touch_pts
    , CAST("POST_TOUCH_AST" AS INTEGER) AS post_touch_ast
    , CAST("POST_TOUCH_TOV" AS INTEGER) AS post_touch_tov
    , CAST("POST_TOUCH_FOULS" AS INTEGER) AS post_touch_fouls
FROM source