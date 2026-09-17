WITH source AS (
    SELECT *
    FROM {{ source('raw_nba', 'player_info')}}
)
SELECT DISTINCT CAST(_extract_season AS VARCHAR) AS season
    , CAST(_extract_league_id AS VARCHAR) AS league_id
    , CAST("PERSON_ID" AS VARCHAR) AS player_id
    , CAST("FIRST_NAME" AS VARCHAR) AS first_name 
    , CAST("LAST_NAME" AS VARCHAR) AS last_name
    , CAST("DISPLAY_FIRST_LAST" AS VARCHAR) AS full_name 
    , CAST("BIRTHDATE" AS DATE) AS birthdate
    , CAST("SCHOOL" AS VARCHAR) AS school
    , CAST("COUNTRY" AS VARCHAR) AS country
    , CAST("HEIGHT" AS VARCHAR) AS height 
    , CAST(NULLIF("WEIGHT", '') AS INTEGER) AS weight 
    , CAST("SEASON_EXP" AS VARCHAR) AS season_exp
    , CAST("JERSEY" AS VARCHAR) AS jersey
    , CAST("POSITION" AS VARCHAR) AS position
    , CAST("TEAM_ID" AS VARCHAR) AS team_id 
    , CAST("TEAM_ABBREVIATION" AS VARCHAR) AS team_abbreviation
    , CAST("FROM_YEAR" AS INTEGER) AS from_year
    , CAST("DRAFT_YEAR" AS VARCHAR) AS draft_year
    , CAST("DRAFT_ROUND" AS VARCHAR) AS draft_round
    , CAST("DRAFT_NUMBER" AS VARCHAR) AS draft_number
FROM source