SELECT player_id
    , team_id  
    , season
    , league_id 
    , season_type
    , (ARRAY_AGG(player_name ORDER BY game_date DESC))[1] AS player_name
    , (ARRAY_AGG(team_name ORDER BY game_date DESC))[1] AS team_name
    , MIN(game_date) AS first_game_date
    , MAX(game_date) AS last_game_date
    , MAX(position) AS roster_position
    , COUNT(*) AS games_played 
    , SUM(win_flag) AS wins

    {% for c in player_summed_columns() %}
    , SUM({{ c }}) AS total_{{ c }}
    {% endfor %}

    {% for r in player_weighted_rates() %}
    , SUM({{ r }} * minutes) AS wsum_{{ r }}
    , SUM(CASE WHEN {{ r }} IS NOT NULL THEN minutes END) AS wmin_{{ r }}
    {% endfor %}
FROM {{ ref('int_player_games_with_opponent')  }}
GROUP BY 1, 2, 3, 4, 5
