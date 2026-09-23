WITH source AS (
    SELECT *FROM {{ source('raw_nba', 'shot_chart_detail') }}
)
SELECT DISTINCT CAST(_extract_season AS VARCHAR) AS season
    , CAST(_extract_league_id AS VARCHAR) AS league_id
    , CAST(_extract_season_type AS VARCHAR) AS season_type
    , CAST("GAME_ID" AS VARCHAR) AS game_id
    , CAST("GAME_EVENT_ID" AS VARCHAR) AS game_event_id
    , CAST("PLAYER_ID" AS VARCHAR) AS player_id
    , CAST("PLAYER_NAME" AS VARCHAR) AS player_name
    , CAST("TEAM_ID" AS VARCHAR) AS team_id 
    , CAST("TEAM_NAME" AS VARCHAR) AS team_name
    , CAST("PERIOD" AS INTEGER) AS quarter 
    , CAST("MINUTES_REMAINING" AS INTEGER) AS minutes_remaining
    , CAST("SECONDS_REMAINING" AS INTEGER) AS seconds_remaining
    , CAST("EVENT_TYPE" AS VARCHAR) AS event_type
    , CAST("ACTION_TYPE" AS VARCHAR) AS action_type
    , CAST("SHOT_TYPE" AS VARCHAR) AS shot_type
    , CAST("SHOT_ZONE_BASIC" AS VARCHAR) AS shot_zone_basic
    , CAST("SHOT_ZONE_AREA" AS VARCHAR) AS shot_zone_area
    , CAST("SHOT_ZONE_RANGE" AS VARCHAR) AS shot_zone_range
    , CAST("SHOT_DISTANCE" AS INTEGER) AS shot_distance
    , CAST("LOC_X" AS INTEGER) AS loc_x
    , CAST("LOC_Y" AS INTEGER) AS loc_y
    , CAST("SHOT_ATTEMPTED_FLAG" AS INTEGER) AS shot_attempted_flag
    , CAST("SHOT_MADE_FLAG" AS INTEGER) AS shot_made_flag
    , CAST("GAME_DATE" AS VARCHAR) AS game_date 
FROM source