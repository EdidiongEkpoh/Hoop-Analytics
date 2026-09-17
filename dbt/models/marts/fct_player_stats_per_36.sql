SELECT player_id, player_name, team_id, team_name, season, league_id, season_type, games_played, minutes_per_game
    , {{  per_x_stat('pts_per_game', 'minutes_per_game', 36)  }} AS pts_per_36
    , {{  per_x_stat('avg_fgm', 'minutes_per_game', 36)  }} AS fgm_per_36
    , {{  per_x_stat('avg_fga', 'minutes_per_game', 36)  }} AS fga_per_36
    , fg_pct
    , {{  per_x_stat('avg_fg3m', 'minutes_per_game', 36)  }} AS fg3m_per_36
    , {{  per_x_stat('avg_fg3a', 'minutes_per_game', 36)  }} AS fg3a_per_36
    , fg3_pct
    , fg3pr
    , {{  per_x_stat('avg_fg2m', 'minutes_per_game', 36)  }} AS fg2m_per_36
    , {{  per_x_stat('avg_fg2a', 'minutes_per_game', 36)  }} AS fg2a_per_36
    , fg2_pct
    , {{  per_x_stat('avg_ftm', 'minutes_per_game', 36)  }} AS ftm_per_36
    , {{  per_x_stat('avg_fta', 'minutes_per_game', 36)  }} AS fta_per_36
    , ft_pct
    , ftr
    , {{  per_x_stat('orebs_per_game', 'minutes_per_game', 36)  }} AS oreb_per_36
    , {{  per_x_stat('drebs_per_game', 'minutes_per_game', 36)  }} AS dreb_per_36
    , {{  per_x_stat('rebs_per_game', 'minutes_per_game', 36)  }} AS reb_per_36
    , {{  per_x_stat('asts_per_game', 'minutes_per_game', 36)  }} AS ast_per_36
    , {{  per_x_stat('stls_per_game', 'minutes_per_game', 36)  }} AS stl_per_36
    , {{  per_x_stat('blks_per_game', 'minutes_per_game', 36)  }} AS blk_per_36
    , {{  per_x_stat('stks_per_game', 'minutes_per_game', 36)  }} AS stk_per_36
    , {{  per_x_stat('tovs_per_game', 'minutes_per_game', 36)  }} AS tov_per_36
    , {{  per_x_stat('pf_per_game', 'minutes_per_game', 36)  }} AS pf_per_36

    , offensive_rating, defensive_rating, net_rating, assist_pct, ast_to_tov, oreb_pct, dreb_pct
    , reb_pct, tov_pct, efg_pct, ts_pct, relative_ts_pct, usage, stl_pct, blk_pct
FROM {{  ref('fct_player_season_summary')  }}

