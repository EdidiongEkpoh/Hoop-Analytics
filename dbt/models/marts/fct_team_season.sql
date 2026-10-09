{% set scaled_stats = ['pts', 'fgm', 'fga', 'fg3m', 'fg3a', 'ftm', 'fta', 'oreb', 'dreb', 'reb', 'ast'
    , 'stl', 'blk', 'tov', 'pf'] %}
{% set misc_stats = ['pts_fast_break', 'pts_off_tov', 'pts_2nd_chance', 'pts_paint'] %}

WITH t AS (
    SELECT *
    FROM {{ ref('int_team_season_stats') }}
)
, misc AS (
    SELECT team_id 
        , season
        , league_id
        , season_type
        {% for s in misc_stats %}
        , {{ s }} AS total_{{ s }}
        , opp_{{ s }} AS opp_total_{{ s }}
        {% endfor %}
    FROM {{ ref('stg_team_misc_stats') }}
)
SELECT team_id
    , team_name
    , season
    , league_id
    , season_type
    , games_played
    , wins
    , losses
    , wins::NUMERIC / NULLIF(wins + losses, 0) AS win_pct
    , home_wins::NUMERIC / NULLIF(home_games, 0) AS home_win_pct
    , away_wins::NUMERIC / NULLIF(away_games, 0) AS away_win_pct
    , total_possessions
    , opp_total_possessions
    , total_possessions::NUMERIC / NULLIF(games_played, 0) AS possessions_per_game
    , 48 * (total_possessions + opp_total_possessions)::NUMERIC
        / NULLIF(2 * (total_minutes::NUMERIC / 5), 0) AS pace 
    
    , 100.0 * total_pts / NULLIF(total_possessions, 0) AS offensive_rating
    , 100.0 * opp_total_pts / NULLIF(opp_total_possessions, 0) AS defensive_rating
    , 100.0 * total_pts / NULLIF(total_possessions, 0)
        - 100.0 * opp_total_pts / NULLIF(opp_total_possessions, 0) AS net_rating
    
    {% for s in scaled_stats %}
    , total_{{ s }}::NUMERIC / NULLIF(games_played, 0) AS {{ s }}_per_game
    , 100.0 * total_{{ s }} / NULLIF(total_possessions, 0) AS {{ s }}_per_100
    , opp_total_{{ s }}::NUMERIC / NULLIF(games_played, 0) AS opp_{{ s }}_per_game
    , 100.0 * opp_total_{{ s }} / NULLIF(opp_total_possessions, 0) AS opp_{{ s }}_per_100
    {% endfor %}

    , total_fgm::NUMERIC / NULLIF(total_fga, 0) AS fg_pct
    , total_fg2m::NUMERIC / NULLIF(total_fg2a, 0) AS fg2_pct
    , total_fg3m::NUMERIC / NULLIF(total_fg3a, 0) AS fg3_pct
    , total_ftm::NUMERIC / NULLIF(total_fta, 0) AS ft_pct
    , total_fg3a::NUMERIC / NULLIF(total_fga, 0) AS fg3pr
    , total_pts::NUMERIC / NULLIF(2 * (total_fga + 0.44 * total_fta), 0) AS ts_pct
    , total_ast::NUMERIC / NULLIF(total_fgm, 0) AS assist_pct
    , total_ast::NUMERIC / NULLIF(total_tov, 0) AS ast_to_tov

    , opp_total_fgm::NUMERIC / NULLIF(opp_total_fga, 0) AS opp_fg_pct
    , opp_total_fg3m::NUMERIC / NULLIF(opp_total_fg3a, 0) AS opp_fg3_pct
    , opp_total_ftm::NUMERIC / NULLIF(opp_total_fta, 0) AS opp_ft_pct
    , opp_total_fg3a::NUMERIC / NULLIF(opp_total_fga, 0) AS opp_fg3pr
    , opp_total_pts::NUMERIC / NULLIF(2 * (opp_total_fga + 0.44 * opp_total_fta), 0) AS opp_ts_pct

    , (total_fgm + 0.5 * total_fg3m)::NUMERIC / NULLIF(total_fga, 0) AS efg_pct
    , total_tov::NUMERIC / NULLIF(total_fga + 0.44 * total_fta + total_tov, 0) AS tov_pct
    , total_oreb::NUMERIC / NULLIF(total_oreb + opp_total_dreb, 0) AS oreb_pct
    , total_fta::NUMERIC / NULLIF(total_fga, 0) AS ftr

    , (opp_total_fgm + 0.5 * opp_total_fg3m)::NUMERIC / NULLIF(opp_total_fga, 0) AS opp_efg_pct
    , opp_total_tov::NUMERIC / NULLIF(opp_total_fga + 0.44 * opp_total_fta + opp_total_tov, 0) AS opp_tov_pct
    , total_dreb::NUMERIC / NULLIF(total_dreb + opp_total_oreb, 0) AS dreb_pct
    , opp_total_fta::NUMERIC / NULLIF(opp_total_fga, 0) AS opp_ftr

    , total_reb::NUMERIC / NULLIF(total_reb + opp_total_reb, 0) AS reb_pct

    {% for s in misc_stats %}
    , total_{{ s }}::NUMERIC / NULLIF(games_played, 0) AS {{ s }}_per_game
    , total_{{ s }}::NUMERIC / NULLIF(total_pts, 0) AS {{ s }}_share
    , opp_total_{{ s }}::NUMERIC / NULLIF(games_played, 0) AS opp_{{ s }}_per_game
    , opp_total_{{ s }}::NUMERIC / NULLIF(opp_total_pts, 0) AS opp_{{ s }}_share
    {% endfor %}
FROM t
LEFT JOIN misc USING (team_id, season, league_id, season_type)



