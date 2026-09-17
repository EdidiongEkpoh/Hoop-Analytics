WITH player_games AS (
    SELECT *
    FROM {{ ref('int_player_game_logs') }}
)
, team_context AS (
    SELECT game_id
        , team_id
        , minutes AS team_minutes
        , opponent_possessions
        , opponent_fga
        , opponent_fg3a
    FROM {{ ref('int_team_games_with_opponent') }}
)
SELECT pg.*
    , tc.team_minutes
    , tc.opponent_possessions
    , tc.opponent_fga
    , tc.opponent_fg3a
    , ROUND(pg.stl * (tc.team_minutes::NUMERIC / 5) / NULLIF(pg.minutes * tc.opponent_possessions, 0), 2) AS stl_pct
    , ROUND(pg.blk * (tc.team_minutes::NUMERIC / 5) / NULLIF(pg.minutes * tc.opponent_possessions, 0), 2) AS blk_pct
FROM player_games pg
LEFT JOIN team_context tc ON tc.game_id = pg.game_id
    AND tc.team_id = pg.team_id