WITH source AS (
    SELECT *
    FROM {{ source('raw_nba', 'shot_zone_league_averages') }}
)
SELECT CAST(_extract_season AS VARCHAR) AS season
    , CAST(_extract_league_id AS VARCHAR) AS league_id
    , CAST(_extract_season_type AS VARCHAR) AS season_type
    , CAST("SHOT_ZONE_BASIC" AS VARCHAR) AS shot_zone_basic
    , CAST("SHOT_ZONE_AREA" AS VARCHAR) AS shot_zone_area
    , CAST("SHOT_ZONE_RANGE" AS VARCHAR) AS shot_zone_range
    , CAST("FGA" AS INTEGER) AS fga 
    , CAST("FGM" AS INTEGER) AS fgm 
    , CAST("FG_PCT" AS FLOAT) AS fg_pct
FROM source