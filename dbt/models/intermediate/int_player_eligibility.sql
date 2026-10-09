{{ config(materialized='table') }}

{% set min_games_pct = var('eligibility_min_games_pct', 0.35) %}
{% set playoff_min_games_pct = var('eligibility_playoff_min_games_pct', 0.5) %}
{% set min_mpg = var('eligibility_min_mpg', 10) %}
WITH player_totals AS (
    SELECT player_id
        , season
        , league_id
        , season_type
        , COUNT(*) AS total_games_played
        , SUM(minutes) AS total_minutes
        , MAX(team_id) AS playoff_team_id
    FROM {{ ref('int_player_game_logs') }}
    GROUP BY 1, 2, 3, 4
)
, team_games AS (
    SELECT team_id
        , season
        , league_id
        , season_type
        , COUNT(*) AS team_games
    FROM {{ ref('int_team_game_logs') }}
    GROUP BY 1, 2, 3, 4
)
, flags AS (
    SELECT pt.player_id
        , pt.season
        , pt.league_id
        , pt.season_type
        , pt.total_games_played
        , pt.total_minutes
        , pt.total_minutes::NUMERIC / NULLIF(pt.total_games_played, 0) AS minutes_per_game
        , COALESCE(
            CASE   
                WHEN pt.season_type = 'Playoffs'
                    THEN pt.total_games_played >= CEIL({{ playoff_min_games_pct }} * tg.team_games)
                ELSE pt.total_games_played >= CEIL({{ min_games_pct }} * sl.season_length)
            END
        , FALSE) AS meets_min_games_threshold
        , COALESCE(
            pt.total_minutes::NUMERIC / NULLIF(pt.total_games_played, 0) >= {{ min_mpg }}
            , FALSE
        ) AS meets_min_minutes_threshold
    FROM player_totals pt
    LEFT JOIN {{ ref('int_season_game_counts') }} sl ON sl.season = pt.season
        AND sl.league_id = pt.league_id
        AND sl.season_type = pt.season_type
    LEFT JOIN team_games tg ON tg.team_id = pt.playoff_team_id
        AND tg.season = pt.season
        AND tg.league_id = pt.league_id
        AND tg.season_type = pt.season_type
)
SELECT *
    , meets_min_games_threshold AND meets_min_minutes_threshold AS is_eligible
FROM flags