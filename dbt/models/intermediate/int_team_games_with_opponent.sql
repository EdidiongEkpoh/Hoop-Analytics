WITH team_games AS (
    SELECT *
    FROM {{ ref('int_team_game_logs') }}
)
SELECT tg.* 
    , opp.team_id AS opponent_team_id
    , opp.team_name AS opponent_team_name
    , opp.pts AS opponent_pts 
    , opp.fgm AS opponent_fgm
    , opp.fga AS opponent_fga
    , opp.fg_pct AS opponent_fg_pct 
    , opp.fg3m AS opponent_fg3m
    , opp.fg3a AS opponent_fg3a
    , opp.fg3_pct AS opponent_fg3_pct
    , ROUND(opp.fg3a::NUMERIC / NULLIF(opp.fga, 0), 3) AS opp_fg3pr
    , opp.fgm - opp.fg3m AS opp_fg2m
    , opp.fga - opp.fg3a AS opp_fg2a
    , opp.ftm AS opponent_ftm
    , opp.fta AS opponent_fta
    , opp.ft_pct AS opponent_ft_pct 
    , ROUND(opp.fta::NUMERIC / NULLIF(opp.fga, 0), 3) AS opp_ftr
    , opp.oreb AS opponent_oreb
    , opp.dreb AS opponent_dreb
    , opp.reb AS opponent_reb
    , opp.ast AS opponent_ast
    , opp.stl AS opponent_stl 
    , opp.blk AS opponent_blk 
    , opp.stk AS opponent_stks
    , opp.tov AS opponent_tov
    , opp.pf AS opponent_pf
    , opp.offensive_rating AS opponent_offensive_rating
    , opp.defensive_rating AS opponent_defensive_rating
    , opp.net_rating AS opponent_net_rating
    , opp.assist_pct AS opponent_assist_pct
    , opp.ast_to_tov AS opponent_ast_to_tov
    , opp.oreb_pct AS opponent_oreb_pct
    , opp.dreb_pct AS opponent_dreb_pct
    , opp.reb_pct AS opponent_reb_pct
    , opp.tov_pct AS opponent_tov_pct
    , opp.ts_pct AS opponent_ts_pct 
    , opp.efg_pct AS opponent_efg_pct
    , opp.pace AS opponent_pace 
    , opp.possessions AS opponent_possessions
FROM team_games tg
JOIN team_games opp 
    ON tg.game_id = opp.game_id AND tg.team_id != opp.team_id