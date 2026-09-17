WITH totals AS (
    SELECT season 
        , league_id
        , season_type
        , SUM(pts) AS total_pts
        , SUM(fga) AS total_fga
        , SUM(fta) AS total_fta
    FROM {{  ref('int_player_game_logs')  }}
    GROUP BY 1, 2, 3
)


select season
	, league_id
	, season_type
	, total_pts / NULLIF(2 * (total_fga + 0.44 * total_fta), 0) as league_ts_pct
FROM totals
