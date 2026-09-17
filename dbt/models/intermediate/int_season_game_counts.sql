WITH team_game_counts AS (
    SELECT team_id 
        , season 
        , league_id 
        , season_type 
        , COUNT(*) AS games_played 
    FROM {{  ref('int_team_game_logs')  }}
    GROUP BY 1, 2, 3, 4
)
SELECT season 
    , league_id 
    , season_type
    , MAX(games_played) AS season_length
FROM team_game_counts
GROUP BY 1, 2, 3