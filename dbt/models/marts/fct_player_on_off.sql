{% set metrics = [
    'offensive_rating', 'defensive_rating', 'net_rating', 'pace', 'efg_pct'
    , 'tov_pct', 'oreb_pct', 'ftr', 'fg3pr', 'ast_pct', 'opp_efg_pct',
    'opp_tov_pct', 'dreb_pct', 'opp_ftr', 'opp_fg3pr'
] %}

WITH s AS (
    SELECT team_id
        , player_id
        , player_name
        , season
        , league_id
        , season_type
        , court_status
        , minutes
        , plus_minus
        , (team_est_poss + opp_est_poss) / 2.0 AS possessions
        , 100.0 * pts / NULLIF((team_est_poss + opp_est_poss) / 2.0, 0) AS offensive_rating
        , 100.0 * opp_pts / NULLIF((team_est_poss + opp_est_poss) / 2.0, 0) AS defensive_rating
        , 100.0 * (pts - opp_pts) / NULLIF((team_est_poss + opp_est_poss) / 2.0, 0) AS net_rating
        , 48.0 * (team_est_poss + opp_est_poss) / 2.0 / NULLIF(minutes, 0) AS pace 

        , (fgm + 0.5 * fg3m) / NULLIF(fga, 0) AS efg_pct
        , tov / NULLIF(team_est_poss, 0) AS tov_pct 
        , oreb / NULLIF(oreb + opp_dreb, 0) AS oreb_pct 
        , fta / NULLIF(fga, 0) AS ftr 
        , fg3a / NULLIF(fga, 0) AS fg3pr
        , ast / NULLIF(fgm, 0) AS ast_pct 
        
        , (opp_fgm + 0.5 * opp_fg3m) / NULLIF(opp_fga, 0) AS opp_efg_pct
        , opp_tov / NULLIF(opp_est_poss, 0) AS opp_tov_pct 
        , dreb / NULLIF(dreb + opp_oreb, 0) AS dreb_pct 
        , opp_fta / NULLIF(opp_fga, 0) AS opp_ftr 
        , opp_fg3a / NULLIF(opp_fga, 0) AS opp_fg3pr
    FROM {{ ref('int_player_on_off') }}
)
, on_court AS (
    SELECT *
    FROM s
    WHERE court_status = 'On'
)
, off_court AS (
    SELECT *
    FROM s
    WHERE court_status = 'Off'
)
SELECT team_id
    , player_id
    , on_court.player_name
    , season
    , league_id
    , season_type
    , on_court.minutes AS minutes_on
    , off_court.minutes AS minutes_off
    , on_court.possessions AS possessions_on
    , off_court.possessions AS possessions_off
    , on_court.minutes / NULLIF(on_court.minutes + off_court.minutes, 0) AS on_court_share
    , on_court.plus_minus AS on_plus_minus
    , off_court.plus_minus AS off_plus_minus
    {% for m in metrics %}
    , on_court.{{ m }} AS on_{{ m }}
    , off_court.{{ m }} AS off_{{ m }}
    , on_court.{{ m }} - off_court.{{ m }} AS {{ m }}_diff
    {% endfor %}
FROM on_court 
LEFT JOIN off_court USING (team_id, player_id, season, season_type, league_id)