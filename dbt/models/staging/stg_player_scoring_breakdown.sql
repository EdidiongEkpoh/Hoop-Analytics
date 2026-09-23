WITH source AS (
    SELECT *
    FROM {{ source('raw_nba', 'player_scoring_breakdown') }}
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
    , CAST("PCT_PTS_PAINT" AS FLOAT) AS pct_pts_paint
    , CAST("PCT_UAST_2PM" AS FLOAT) AS pct_uast_2pm
    , CAST("PCT_AST_2PM" AS FLOAT) AS pct_ast_2pm
    , CAST("PCT_UAST_3PM" AS FLOAT) AS pct_uast_3pm
    , CAST("PCT_AST_3PM" AS FLOAT) AS pct_ast_3pm
    , CAST("PCT_UAST_FGM" AS FLOAT) AS pct_uast_fgm
    , CAST("PCT_AST_FGM" AS FLOAT) AS pct_ast_fgm
FROM source