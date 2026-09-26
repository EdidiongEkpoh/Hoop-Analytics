{{ config(materialized='table') }}

WITH season_totals AS (
    SELECT player_id
        , season
        , league_id
        , season_type
        , SUM(games_played) AS total_games_played
    FROM {{  ref('int_player_season_stats')  }}
    GROUP BY 1, 2, 3, 4
)
SELECT st.player_id
    , st.season
    , st.league_id
    , st.season_type
    , st.total_games_played
    , CASE 
        WHEN st.season_type = 'Regular Season' THEN st.total_games_played >= CEIL(0.35 * sl.season_length)
        ELSE TRUE
      END AS meets_min_games_threshold
FROM season_totals st
LEFT JOIN {{  ref('int_season_game_counts')  }} sl ON sl.season = st.season 
    AND sl.league_id = st.league_id
    AND st.season_type = sl.season_type
