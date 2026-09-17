SELECT player_id, player_name, team_id, team_name, season, league_id, season_type, games_played, minutes_per_game
    , {{  per_x_stat('pts_per_game', 'possessions_per_game', 75)  }} AS pts_per_75
    , {{  per_x_stat('avg_fgm', 'possessions_per_game', 75)  }} AS fgm_per_75
    , {{  per_x_stat('avg_fga', 'possessions_per_game', 75)  }} AS fga_per_75
    , fg_pct
    , {{  per_x_stat('avg_fg3m', 'possessions_per_game', 75)  }} AS fg3m_per_75
    , {{  per_x_stat('avg_fg3a', 'possessions_per_game', 75)  }} AS fg3a_per_75
    , fg3_pct
    , fg3pr
    , {{  per_x_stat('avg_fg2m', 'possessions_per_game', 75)  }} AS fg2m_per_75
    , {{  per_x_stat('avg_fg2a', 'possessions_per_game', 75)  }} AS fg2a_per_75
    , fg2_pct
    , {{  per_x_stat('avg_ftm', 'possessions_per_game', 75)  }} AS ftm_per_75
    , {{  per_x_stat('avg_fta', 'possessions_per_game', 75)  }} AS fta_per_75
    , ft_pct
    , ftr
    , {{  per_x_stat('orebs_per_game', 'possessions_per_game', 75)  }} AS oreb_per_75
    , {{  per_x_stat('drebs_per_game', 'possessions_per_game', 75)  }} AS dreb_per_75
    , {{  per_x_stat('rebs_per_game', 'possessions_per_game', 75)  }} AS reb_per_75
    , {{  per_x_stat('asts_per_game', 'possessions_per_game', 75)  }} AS ast_per_75
    , {{  per_x_stat('stls_per_game', 'possessions_per_game', 75)  }} AS stl_per_75
    , {{  per_x_stat('blks_per_game', 'possessions_per_game', 75)  }} AS blk_per_75
    , {{  per_x_stat('stks_per_game', 'possessions_per_game', 75)  }} AS stk_per_75
    , {{  per_x_stat('tovs_per_game', 'possessions_per_game', 75)  }} AS tov_per_75
    , {{  per_x_stat('pf_per_game', 'possessions_per_game', 75)  }} AS pf_per_75

    , offensive_rating, defensive_rating, net_rating, assist_pct, ast_to_tov, oreb_pct, dreb_pct
    , reb_pct, tov_pct, efg_pct, ts_pct, relative_ts_pct, usage, stl_pct, blk_pct
FROM {{  ref('fct_player_season_summary')  }}

