WITH source AS (
    SELECT *
    FROM {{ source('raw_nba', 'players')}}
)
SELECT DISTINCT CAST("id" AS VARCHAR) AS id
    , CAST("first_name" AS VARCHAR) AS first_name 
    , CAST("last_name" AS VARCHAR) AS last_name
    , CAST("full_name" AS VARCHAR) AS full_name 
FROM source