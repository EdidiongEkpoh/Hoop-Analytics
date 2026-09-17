WITH opp AS (
    SELECT *
    FROM {{ ref('int_team_season_opponent_stats') }}
)
, own AS (
    SELECT team_id
        , season
        , league_id
        , season_type
        , possessions_per_game
    FROM {{ ref('int_team_season_stats') }}
)
SELECT o.team_id, o.season, o.league_id, o.season_type, o.games_played, own.possessions_per_game
    , {{ per_x_stat('o.opp_pts_per_game', 'own.possessions_per_game', 100) }} AS opp_pts_per_100
    , {{ per_x_stat('o.opp_avg_fgm', 'own.possessions_per_game', 100) }} AS opp_fgm_per_100
    , {{ per_x_stat('o.opp_avg_fga', 'own.possessions_per_game', 100) }} AS opp_fga_per_100
    , {{ per_x_stat('o.opp_avg_fg3m', 'own.possessions_per_game', 100) }} AS opp_fg3m_per_100
    , {{ per_x_stat('o.opp_avg_fg3a', 'own.possessions_per_game', 100) }} AS opp_fg3a_per_100
    , {{ per_x_stat('o.opp_avg_ftm', 'own.possessions_per_game', 100) }} AS opp_ftm_per_100
    , {{ per_x_stat('o.opp_avg_fta', 'own.possessions_per_game', 100) }} AS opp_fta_per_100

    , {{ per_x_stat('o.opp_oreb_per_game', 'own.possessions_per_game', 100) }} AS opp_oreb_per_100
    , {{ per_x_stat('o.opp_dreb_per_game', 'own.possessions_per_game', 100) }} AS opp_dreb_per_100
    , {{ per_x_stat('o.opp_reb_per_game', 'own.possessions_per_game', 100) }} AS opp_reb_per_100

    , {{ per_x_stat('o.opp_ast_per_game', 'own.possessions_per_game', 100) }} AS opp_ast_per_100
    , {{ per_x_stat('o.opp_stl_per_game', 'own.possessions_per_game', 100) }} AS opp_stl_per_100
    , {{ per_x_stat('o.opp_blk_per_game', 'own.possessions_per_game', 100) }} AS opp_blk_per_100
    , {{ per_x_stat('o.opp_tov_per_game', 'own.possessions_per_game', 100) }} AS opp_tov_per_100
    , {{ per_x_stat('o.opp_pf_per_game', 'own.possessions_per_game', 100) }} AS opp_pf_per_100

    , o.opp_fg_pct, o.opp_fg3_pct, o.opp_fg3pr, o.opp_ft_pct, o.opp_ftr
    , o.opp_offensive_rating, o.opp_defensive_rating, o.opp_net_rating
    , o.opp_ast_pct, o.opp_ast_to_tov, o.opp_oreb_pct, o.opp_dreb_pct, o.opp_reb_pct, o.opp_tov_pct
    , o.opp_ts_pct, o.opp_efg_pct
FROM opp o
LEFT JOIN own ON own.team_id = o.team_id 
    AND own.season = o.season
    AND own.league_id = o.league_id
    AND own.season_type = o.season_type