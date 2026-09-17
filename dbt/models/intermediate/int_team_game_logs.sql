WITH basic AS (
    SELECT *
    FROM {{ ref('stg_team_basic_boxscores') }}
)
, advanced AS (
    SELECT *
    FROM {{ ref('stg_team_advanced_boxscores') }}
)
SELECT b.game_id 
    , b.team_id 
    , b.team_name
    , b.season 
    , b.league_id
    , b.season_type
    , b.game_date
    , b.matchup
    , CASE WHEN b.matchup LIKE '%@%' THEN 'Away' ELSE 'Home' END AS home_away
    , b.wl 
    , CASE WHEN b.wl = 'W' THEN 1 ELSE 0 END AS win_flag 
    , CASE WHEN b.wl = 'L' THEN 1 ELSE 0 END AS loss_flag 
    , b.minutes
    , b.pts 
    , b.fgm
    , b.fga 
    , b.fg_pct
    , b.fg3m 
    , b.fg3a
    , b.fg3_pct
    , ROUND(b.fg3a::NUMERIC / NULLIF(b.fga, 0), 3) AS fg3pr
    , b.fgm - b.fg3m AS fg2m
    , b.fga - b.fg3a AS fg2a
    , b.ftm 
    , b.fta 
    , b.ft_pct 
    , ROUND(b.fta::NUMERIC / NULLIF(b.fga, 0), 3) AS ftr
    , b.oreb 
    , b.dreb 
    , b.reb 
    , b.ast 
    , b.stl 
    , b.blk 
    , b.stl + b.blk AS stk
    , b.tov 
    , b.pf 
    , b.plus_minus 
    , a.offensive_rating
    , a.defensive_rating 
    , a.net_rating 
    , a.assist_pct
    , a.ast_to_tov
    , a.oreb_pct
    , a.dreb_pct 
    , a.reb_pct 
    , a.tov_pct
    , a.ts_pct 
    , a.efg_pct 
    , a.pace 
    , a.possessions 
FROM basic b 
LEFT JOIN advanced a ON a.game_id = b.game_id 
    AND a.team_id = b.team_id