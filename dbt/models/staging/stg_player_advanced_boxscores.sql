WITH source AS (
    SELECT *
    FROM {{ source('raw_nba', 'player_advanced_boxscores')}}
)
, deduped AS (
    SELECT *
        , ROW_NUMBER() OVER (PARTITION BY "gameId", "personId" ORDER BY "possessions" DESC) AS rn
    FROM source
)
SELECT DISTINCT CAST(_extract_season AS VARCHAR) AS season
    , CAST(_extract_league_id AS VARCHAR) AS league_id
    , CAST(_extract_season_type AS VARCHAR) AS season_type
    , CAST("gameId" AS VARCHAR) AS game_id 
    , CAST("teamId" AS VARCHAR) AS team_id 
    , CAST("teamCity" AS VARCHAR) AS team_city
    , CAST("teamName" AS VARCHAR) AS team_name 
    , CAST("personId" AS VARCHAR) AS player_id
    , CAST("firstName" AS VARCHAR) AS first_name 
    , CAST("familyName" AS VARCHAR) AS last_name
    , CAST("comment" AS VARCHAR) AS comment
    , CAST("minutes" AS VARCHAR) AS minutes 
    , CAST("offensiveRating" AS FLOAT) AS offensive_rating
    , CAST("defensiveRating" AS FLOAT) AS defensive_rating
    , CAST("netRating" AS FLOAT) AS net_rating
    , CAST("assistPercentage" AS FLOAT) AS assist_pct
    , CAST("assistToTurnover" AS FLOAT) AS ast_to_tov
    , CAST("offensiveReboundPercentage" AS FLOAT) AS oreb_pct
    , CAST("defensiveReboundPercentage" AS FLOAT) AS dreb_pct
    , CAST("reboundPercentage" AS FLOAT) AS reb_pct
    , CAST("turnoverRatio" AS FLOAT) AS tov_pct
    , CAST("effectiveFieldGoalPercentage" AS FLOAT) AS efg_pct
    , CAST("trueShootingPercentage" AS FLOAT) AS ts_pct
    , CAST("usagePercentage" AS FLOAT) AS usage
    , CAST("pace" AS FLOAT) AS pace 
    , CAST("possessions" AS INTEGER) AS possessions
FROM deduped
WHERE rn = 1