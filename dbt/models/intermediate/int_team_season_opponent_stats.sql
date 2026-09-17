SELECT team_id
    , season
    , league_id
    , season_type
    , COUNT(*) AS games_played
    , AVG(opponent_pts) AS opp_pts_per_game
    , AVG(opponent_fgm) AS opp_avg_fgm
    , AVG(opponent_fga) AS opp_avg_fga
    , AVG(opponent_fg_pct) AS opp_fg_pct
    , AVG(opponent_fg3m) AS opp_avg_fg3m
    , AVG(opponent_fg3a) AS opp_avg_fg3a
    , AVG(opponent_fg3_pct) AS opp_fg3_pct
    , AVG(opp_fg3pr) AS opp_fg3pr
    , AVG(opponent_ftm) AS opp_avg_ftm
    , AVG(opponent_fta) AS opp_avg_fta
    , AVG(opponent_ft_pct) AS opp_ft_pct
    , AVG(opp_ftr) AS opp_ftr
    , AVG(opponent_oreb) AS opp_oreb_per_game
    , AVG(opponent_dreb) AS opp_dreb_per_game
    , AVG(opponent_reb) AS opp_reb_per_game
    , AVG(opponent_ast) AS opp_ast_per_game
    , AVG(opponent_stl) AS opp_stl_per_game
    , AVG(opponent_blk) AS opp_blk_per_game
    , AVG(opponent_tov) AS opp_tov_per_game
    , AVG(opponent_pf) AS opp_pf_per_game
    , AVG(opponent_offensive_rating) AS opp_offensive_rating
    , AVG(opponent_defensive_rating) AS opp_defensive_rating
    , AVG(opponent_net_rating) AS opp_net_rating
    , AVG(opponent_assist_pct) AS opp_ast_pct
    , AVG(opponent_ast_to_tov) AS opp_ast_to_tov
    , AVG(opponent_oreb_pct) AS opp_oreb_pct
    , AVG(opponent_dreb_pct) AS opp_dreb_pct
    , AVG(opponent_reb_pct) AS opp_reb_pct
    , AVG(opponent_tov_pct) AS opp_tov_pct
    , AVG(opponent_ts_pct) AS opp_ts_pct
    , AVG(opponent_efg_pct) AS opp_efg_pct
FROM {{ ref('int_team_games_with_opponent') }}
GROUP BY 1, 2, 3,4