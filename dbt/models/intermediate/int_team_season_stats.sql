SELECT team_id  
    , team_name
    , season
    , league_id 
    , season_type
    , COUNT(*) AS games_played 
    , SUM(win_flag) AS wins
    , SUM(loss_flag) AS losses
    , ROUND(SUM(win_flag) * 100.0 / NULLIF(SUM(win_flag) + SUM(loss_flag), 0), 2) AS win_pct
    , AVG(pts) AS pts_per_game
    , AVG(fgm) AS avg_fgm
    , AVG(fga) AS avg_fga 
    , AVG(fg_pct) AS fg_pct 
    , AVG(fg3m) AS avg_fg3m
    , AVG(fg3a) AS avg_fg3a
    , AVG(fg3_pct) AS fg3_pct
    , AVG(fg3pr) AS fg3pr
    , AVG(fg2m) AS avg_fg2m
    , AVG(fg2a) AS avg_fg2a
    , (SUM(fg2m) * 100.0) / NULLIF(SUM(fg2a), 0) AS fg2_pct
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
    , AVG(offensive_rating) AS offensive_rating
    , AVG(defensive_rating) AS defensive_rating
    , AVG(net_rating) AS net_rating 
    , AVG(assist_pct) AS assist_pct 
    , AVG(ast_to_tov) AS ast_to_tov
    , AVG(oreb_pct) AS oreb_pct
    , AVG(dreb_pct) AS dreb_pct
    , AVG(reb_pct) AS reb_pct
    , AVG(tov_pct) AS tov_pct
    , AVG(pace) AS pace
    , AVG(possessions) AS possessions_per_game
    , AVG(efg_pct) AS efg_pct
    , AVG(ts_pct) AS ts_pct
    , AVG(CASE WHEN home_away = 'Home' THEN win_flag END) AS home_win_pct
    , AVG(CASE WHEN home_away = 'Away' THEN win_flag END) AS away_win_pct
FROM {{ ref('int_team_game_logs')  }}
GROUP BY 1, 2, 3, 4, 5