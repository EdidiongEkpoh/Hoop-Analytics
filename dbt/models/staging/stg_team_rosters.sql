{{ config(materialized='table') }}
WITH source AS (
    SELECT *
    FROM {{ source('raw_nba', 'team_rosters')}}
)
SELECT DISTINCT CAST("TeamID" AS VARCHAR) AS team_id
    , CAST("LeagueID" AS VARCHAR) AS league_id_code
    , CAST(_extract_season AS VARCHAR) AS season
    , CAST(_extract_league_id AS VARCHAR) AS league_id
    , CAST("PLAYER_ID" AS VARCHAR) AS player_id
    , CAST("PLAYER" AS VARCHAR) AS player_name
    , CAST("NUM" AS VARCHAR) AS jersey_number
    , CAST("POSITION" AS VARCHAR) AS position
    , CAST("HEIGHT" AS VARCHAR) AS height
    , CAST("WEIGHT" AS INTEGER) AS weight 
    , CAST("BIRTH_DATE" AS VARCHAR) AS birthdate
    , CAST("AGE" AS INTEGER) AS age
    , CAST("EXP" AS VARCHAR) AS player_exp
    , CAST("SCHOOL" AS VARCHAR) AS school
    , CAST("HOW_ACQUIRED" AS VARCHAR) AS how_acquired
FROM source