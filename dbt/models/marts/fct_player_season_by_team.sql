WITH metrics AS (
    SELECT player_id
        , player_name
        , team_id
        , team_name
        , season
        , league_id
        , season_type
        , first_game_date
        , last_game_date
        , roster_position
        , {{ player_season_metrics() }}
    FROM {{ ref('int_player_season_stats') }}
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