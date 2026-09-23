WITH source AS (
    SELECT *
    FROM {{ source('raw_nba', 'standings') }}
)
SELECT DISTINCT CAST("LeagueID" AS VARCHAR) AS league_id_code
    , CAST("SeasonID" AS VARCHAR) AS season_id_code
    , CAST(_extract_season AS VARCHAR) AS season
    , CAST(_extract_league_id AS VARCHAR) AS league_id
    , CAST(_extract_season_type AS VARCHAR) AS season_type
    , CAST("TeamID" AS VARCHAR) AS team_id
    , CAST("TeamCity" AS VARCHAR) AS team_city
    , CAST("TeamName" AS VARCHAR) AS team_name 
    , CAST("Record" AS VARCHAR) AS record
    , CAST("Conference" AS VARCHAR) AS conference
    , CAST("ConferenceRecord" AS VARCHAR) AS conference_record 
    , CAST("Division" AS VARCHAR) AS division
    , CAST("DivisionRecord" AS VARCHAR) AS division_record
    , CAST("WINS" AS INTEGER) AS wins 
    , CAST("LOSSES" AS INTEGER) AS losses
    , CAST("WinPCT" AS FLOAT) AS win_pct
    , CAST("LeagueRank" AS INTEGER) AS league_rank
    , CAST("ConferenceGamesBack" AS INTEGER) AS conference_games_back
    , CAST("DivisionGamesBack" AS INTEGER) AS division_games_back
    , CAST("ClinchIndicator" AS VARCHAR) AS clinch_indicator
    , CAST("HOME" AS VARCHAR) AS home_record
    , CAST("ROAD" AS VARCHAR) AS road_record
    , CAST("L10" AS VARCHAR) AS last_10_record
    , CAST("OT" AS VARCHAR) AS ot_record
    , CAST("CurrentStreak" AS VARCHAR) AS current_streak
    , CAST("LongWinStreak" AS INTEGER) AS long_win_streak
    , CAST("LongLossStreak" AS INTEGER) AS long_loss_streak
    , CAST("PointsPG" AS FLOAT) AS points_per_game
    , CAST("OppPointsPG" AS FLOAT) AS opp_points_per_game
    , CAST("DiffPointsPG" AS FLOAT) AS point_diff_per_game
FROM source