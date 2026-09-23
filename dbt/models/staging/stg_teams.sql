WITH source AS (
    SELECT *
    FROM {{ source('raw_nba', 'teams')}}
)
SELECT DISTINCT CAST(id AS VARCHAR) AS id
    , CAST(full_name AS VARCHAR) AS full_name 
    , CAST(abbreviation AS VARCHAR) AS abbreviation
    , CAST(nickname AS VARCHAR) AS nickname
    , CAST(city AS VARCHAR) AS city 
    , CAST(state AS VARCHAR) AS state
    , CAST(year_founded AS INTEGER) AS year_founded
FROM source