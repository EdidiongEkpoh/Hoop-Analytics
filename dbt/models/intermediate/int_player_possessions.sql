SELECT player_id
    , team_id
    , season
    , league_id
    , season_type
    , SUM(possessions) AS total_possessions
FROM {{ ref('fct_player_games') }}
GROUP BY 1, 2, 3, 4, 5