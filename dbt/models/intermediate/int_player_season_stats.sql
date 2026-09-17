SELECT player_id
    , player_name
    , team_id  
    , team_name
    , season
    , league_id 
    , season_type
    , COUNT(*) AS games_played 
    , SUM(win_flag) AS wins
    , AVG(pts) AS pts_per_game
    , AVG(fgm) AS avg_fgm
    , AVG(fga) AS avg_fga 
    , AVG(fg_pct) AS fg_pct 
    , AVG(fg3m) AS avg_fg3m
    , AVG(fg3a) AS avg_fg3a
    , COALESCE(AVG(fg3_pct), 0.0) AS fg3_pct
    , AVG(fg3pr) AS fg3pr
    , AVG(fg2m) AS avg_fg2m
    , AVG(fg2a) AS avg_fg2a
    , (SUM(fg2m) * 1.0) / NULLIF(SUM(fg2a), 0) AS fg2_pct
    , AVG(ftm) AS avg_ftm 
    , AVG(fta) AS avg_fta 
    , AVG(ft_pct) AS ft_pct
    , AVG(ftr) AS ftr
    , AVG(oreb) AS orebs_per_game
    , AVG(dreb) AS drebs_per_game
    , AVG(reb) AS rebs_per_game
    , AVG(ast) AS asts_per_game
    , AVG(stl) AS stls_per_game
    , AVG(blk) AS blks_per_game
    , AVG(stk) AS stks_per_game
    , AVG(tov) AS tovs_per_game
    , AVG(pf) AS pf_per_game
    , AVG(minutes) AS minutes_per_game
    , AVG(offensive_rating) AS offensive_rating
    , AVG(defensive_rating) AS defensive_rating
    , AVG(net_rating) AS net_rating 
    , AVG(assist_pct) AS assist_pct 
    , AVG(ast_to_tov) AS ast_to_tov
    , AVG(oreb_pct) AS oreb_pct
    , AVG(dreb_pct) AS dreb_pct
    , AVG(reb_pct) AS reb_pct
    , AVG(tov_pct) AS tov_pct
    , AVG(pace) AS avg_pace
    , AVG(usage) AS usage
    , AVG(possessions) AS possessions_per_game
    , AVG(efg_pct) AS efg_pct
    , AVG(ts_pct) AS ts_pct
    , AVG(stl_pct) AS stl_pct
    , AVG(blk_pct) AS blk_pct
FROM {{ ref('int_player_games_with_opponent')  }}
GROUP BY 1, 2, 3, 4, 5, 6, 7
