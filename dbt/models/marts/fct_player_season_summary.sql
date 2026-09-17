SELECT a.*
    , a.blk_pct + a.stl_pct AS stk_pct
    , a.ts_pct - lsa.league_ts_pct AS relative_ts_pct
FROM {{ ref('int_player_season_stats')  }} a
LEFT JOIN {{ ref('int_league_season_averages')  }} lsa ON lsa.season = a.season
    AND lsa.league_id = a.league_id
    AND lsa.season_type = a.season_type