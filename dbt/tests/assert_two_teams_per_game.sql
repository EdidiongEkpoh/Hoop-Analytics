SELECT game_id
    , COUNT(*) AS team_count
FROM {{  ref('int_team_game_logs')  }}
GROUP BY 1
HAVING COUNT(*) != 2