{{ config(materialized='table') }}
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
, roster_details AS (
    SELECT player_id 
        , team_id
        , position 
        , season
    FROM {{ ref('stg_team_rosters') }}

)
SELECT pg.*
    , rd.position
    , ROUND(pg.fg2m::NUMERIC / NULLIF(pg.fg2a, 0), 3) AS fg2_pct
    , tc.team_minutes
    , tc.opponent_possessions
    , tc.opponent_fga
    , tc.opponent_fg3a
    , pg.minutes * tc.opponent_possessions / NULLIF(tc.team_minutes::NUMERIC / 5, 0.0) AS opp_poss_on_court
    , pg.minutes * (tc.opponent_fga - tc.opponent_fg3a) /  NULLIF(tc.team_minutes::NUMERIC/ 5, 0) AS opp_2pa_on_court
    , pg.stl * (tc.team_minutes::NUMERIC / 5) / NULLIF(pg.minutes * tc.opponent_possessions, 0) AS stl_pct
    , pg.blk * (tc.team_minutes::NUMERIC / 5) / NULLIF(pg.minutes * (tc.opponent_fga - tc.opponent_fg3a), 0) AS blk_pct
FROM player_games pg
LEFT JOIN team_context tc ON tc.game_id = pg.game_id
    AND tc.team_id = pg.team_id
LEFT JOIN roster_details rd ON rd.player_id = pg.player_id
    AND rd.team_id = pg.team_id
    AND rd.season = pg.season
