WITH by_team AS (
    SELECT *
    FROM {{ ref('int_player_season_stats') }}
)
, totals AS (
    SELECT player_id
        , season
        , league_id
        , season_type
        , (ARRAY_AGG(player_name ORDER BY last_game_date DESC))[1] AS player_name
        , (ARRAY_AGG(team_id ORDER BY last_game_date DESC))[1] AS last_team_id
        , (ARRAY_AGG(team_name ORDER BY last_game_date DESC))[1] AS last_team_name
        , (ARRAY_AGG(roster_position ORDER BY last_game_date DESC)
            FILTER (WHERE roster_position IS NOT NULL))[1] AS roster_position
        , COUNT(*) AS teams_played_for
        , SUM(games_played)::INT AS games_played
        , SUM(wins)::INT AS wins

        {% for c in player_summed_columns() %}
        , SUM(total_{{ c }} ) AS total_{{ c }}
        {% endfor %}

        {% for r in player_weighted_rates() %}
        , SUM(wsum_{{ r }}) AS wsum_{{ r }}
        , SUM(wmin_{{ r }}) AS wmin_{{ r }}
        {% endfor %}
    FROM by_team
    GROUP BY 1, 2, 3, 4
)
, metrics AS (
    SELECT player_id
        , player_name
        , season
        , league_id
        , season_type
        , last_team_id
        , last_team_name
        , roster_position
        , teams_played_for
        , {{ player_season_metrics() }}
    FROM totals
)
SELECT m.*
    , COALESCE(pi.position, m.roster_position) AS position
    , {{ position_group('COALESCE(pi.position, m.roster_position)') }} AS position_group
    , m.ts_pct - lsa.league_ts_pct AS relative_ts_pct
    , COALESCE(e.is_eligible, FALSE) AS is_eligible
FROM metrics m 
LEFT JOIN {{ ref('stg_player_info') }} pi ON pi.player_id = m.player_id
    AND pi.season = m.season
    AND pi.league_id = m.league_id
LEFT JOIN {{ ref('int_league_season_averages') }} lsa ON lsa.season = m.season
    AND lsa.league_id = m.league_id
    AND lsa.season_type = m.season_type
LEFT JOIN {{ ref('int_player_eligibility') }} e ON e.player_id = m.player_id
    AND e.season = m.season
    AND e.league_id = m.league_id
    AND e.season_type = m.season_type