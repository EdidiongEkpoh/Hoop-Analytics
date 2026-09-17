SELECT team_id, team_name, season, league_id, season_type, wins, losses, win_pct, games_played, possessions_per_game, pace
    , {{  per_x_stat('pts_per_game', 'possessions_per_game', 100)  }} AS pts_per_100
    , {{  per_x_stat('avg_fgm', 'possessions_per_game', 100)  }} AS fgm_per_100
    , {{  per_x_stat('avg_fga', 'possessions_per_game', 100)  }} AS fga_per_100
    , fg_pct
    , {{  per_x_stat('avg_fg3m', 'possessions_per_game', 100)  }} AS fg3m_per_100
    , {{  per_x_stat('avg_fg3a', 'possessions_per_game', 100)  }} AS fg3a_per_100
    , fg3_pct
    , fg3pr
    , {{  per_x_stat('avg_fg2m', 'possessions_per_game', 100)  }} AS fg2m_per_100
    , {{  per_x_stat('avg_fg2a', 'possessions_per_game', 100)  }} AS fg2a_per_100
    , fg2_pct
    , {{  per_x_stat('avg_ftm', 'possessions_per_game', 100)  }} AS ftm_per_100
    , {{  per_x_stat('avg_fta', 'possessions_per_game', 100)  }} AS fta_per_100
    , ft_pct
    , ftr
    , {{  per_x_stat('orebs_per_game', 'possessions_per_game', 100)  }} AS oreb_per_100
    , {{  per_x_stat('drebs_per_game', 'possessions_per_game', 100)  }} AS dreb_per_100
    , {{  per_x_stat('rebs_per_game', 'possessions_per_game', 100)  }} AS reb_per_100
    , {{  per_x_stat('asts_per_game', 'possessions_per_game', 100)  }} AS ast_per_100
    , {{  per_x_stat('stls_per_game', 'possessions_per_game', 100)  }} AS stl_per_100
    , {{  per_x_stat('blks_per_game', 'possessions_per_game', 100)  }} AS blk_per_100
    , {{  per_x_stat('stks_per_game', 'possessions_per_game', 100)  }} AS stk_per_100
    , {{  per_x_stat('tovs_per_game', 'possessions_per_game', 100)  }} AS tov_per_100
    , {{  per_x_stat('pf_per_game', 'possessions_per_game', 100)  }} AS pf_per_100

    , offensive_rating, defensive_rating, net_rating, assist_pct, ast_to_tov, oreb_pct, dreb_pct
    , reb_pct, tov_pct, efg_pct, ts_pct, home_win_pct, away_win_pct
FROM {{  ref('int_team_season_stats')  }}

