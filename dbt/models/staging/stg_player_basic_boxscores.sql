WITH source AS (
    SELECT *
    FROM {{ source('raw_nba', 'player_basic_boxscores')}}
)
SELECT CAST("SEASON_ID" AS VARCHAR) AS season_id_code
    , CAST(_extract_season AS VARCHAR) AS season
    , CAST(_extract_league_id AS VARCHAR) AS league_id
    , CAST(_extract_season_type AS VARCHAR) AS season_type
    , CAST("PLAYER_ID" AS VARCHAR) AS player_id 
    , CAST("PLAYER_NAME" AS VARCHAR) AS player_name
    , CAST("TEAM_ID" AS VARCHAR) AS team_id 
    , CAST("TEAM_NAME" AS VARCHAR) AS team_name
    , CAST("GAME_ID" AS VARCHAR) AS game_id 
    , CAST("GAME_DATE" AS DATE) AS game_date
    , CAST("MATCHUP" AS VARCHAR) AS matchup
    , CAST("WL" AS VARCHAR) AS wl 
    , CAST("MIN" AS INTEGER) AS minutes 
    , CAST("FGM" AS INTEGER) AS fgm 
    , CAST("FGA" AS INTEGER) AS fga 
    , CAST("FG_PCT" AS FLOAT) AS fg_pct 
    , CAST("FG3M" AS INTEGER) AS fg3m 
    , CAST("FG3A" AS INTEGER) AS fg3a
    , CAST("FG3_PCT" AS FLOAT) AS fg3_pct 
    , CAST("FTM" AS INTEGER) AS ftm 
    , CAST("FTA" AS INTEGER) AS fta
    , CAST("FT_PCT" AS FLOAT) AS ft_pct
    , CAST("OREB" AS INTEGER) AS oreb 
    , CAST("DREB" AS INTEGER) AS dreb 
    , CAST("REB" AS INTEGER) AS reb 
    , CAST("AST" AS INTEGER) AS ast 
    , CAST("STL" AS INTEGER) AS stl
    , CAST("BLK" AS INTEGER) AS blk 
    , CAST("TOV" AS INTEGER) AS tov 
    , CAST("PF" AS INTEGER) AS pf
    , CAST("PTS" AS INTEGER) AS pts 
    , CAST("PLUS_MINUS" AS INTEGER) AS plus_minus 
FROM source