WITH base AS (
    SELECT player_id, season, league_id, season_type
    FROM {{ ref('stg_player_catch_shoot_stats') }}  
    UNION 
    SELECT player_id, season, league_id, season_type
    FROM {{  ref('stg_player_pullup_shooting_stats')  }}
    UNION 
    SELECT player_id, season, league_id, season_type
    FROM {{  ref('stg_player_drives_stats')  }}
    UNION
    SELECT player_id, season, league_id, season_type
    FROM {{  ref('stg_player_postup_stats')  }}
    UNION
    SELECT player_id, season, league_id, season_type
    FROM {{ ref('stg_player_scoring_breakdown')  }}
)
, season_possessions AS (
    SELECT player_id
        , season
        , league_id
        , season_type
        , SUM(total_possessions) AS total_possessions
    FROM {{ ref('int_player_possessions') }}
    GROUP BY 1, 2, 3, 4
)
SELECT b.player_id
    , COALESCE(cs.player_name, pu.player_name, d.player_name, p.player_name, sb.player_name) AS player_name
    , b.season
    , b.league_id
    , b.season_type
    , COALESCE(cs.team_id, pu.team_id, d.team_id, p.team_id, sb.team_id) AS team_id
    , COALESCE(cs.games_played, pu.games_played, d.games_played, p.games_played, sb.games_played) AS games_played
    , COALESCE(cs.minutes, pu.minutes, d.minutes, p.minutes, sb.minutes) AS minutes
    , sp.total_possessions
    , cs.catch_shoot_fgm , cs.catch_shoot_fga
    , cs.catch_shoot_fg_pct
    , cs.catch_shoot_fg3m, cs.catch_shoot_fg3a
    , cs.catch_shoot_fg3_pct    
    , cs.catch_shoot_efg 
    , cs.catch_shoot_pts

    , pu.pullup_fgm, pu.pullup_fga, pu.pullup_fg_pct, pu.pullup_fg3m, pu.pullup_fg3a, pu.pullup_fg3_pct
    , pu.pullup_efg_pct, pu.pullup_pts

    , d.drives
    , d.drive_fgm, d.drive_fga, d.drive_fg_pct, d.drive_ftm, d.drive_fta, d.drive_ft_pct
    , d.drive_pts, d.drive_ast, d.drive_tov, d.drive_pf

    , p.post_touches
    , p.post_touch_fgm, p.post_touch_fga, p.post_touch_fg_pct, p.post_touch_ftm, p.post_touch_fta, p.post_touch_ft_pct
    , p.post_touch_pts, p.post_touch_ast, p.post_touch_tov, p.post_touch_fouls

    , sb.pct_pts_paint, sb.pct_uast_2pm, sb.pct_ast_2pm, sb.pct_uast_3pm, sb.pct_ast_3pm, sb.pct_uast_fgm, sb.pct_ast_fgm
FROM base b
LEFT JOIN {{ ref('stg_player_catch_shoot_stats') }} cs ON cs.player_id = b.player_id
    AND cs.season = b.season
    AND cs.league_id = b.league_id
    AND cs.season_type = b.season_type  
LEFT JOIN {{ ref('stg_player_pullup_shooting_stats') }} pu ON pu.player_id = b.player_id
    AND pu.season = b.season
    AND pu.league_id = b.league_id
    AND pu.season_type = b.season_type
LEFT JOIN {{ ref('stg_player_drives_stats') }} d ON d.player_id = b.player_id
    AND d.season = b.season
    AND d.league_id = b.league_id
    AND d.season_type = b.season_type   
LEFT JOIN {{ ref('stg_player_postup_stats') }} p ON p.player_id = b.player_id
    AND p.season = b.season
    AND p.league_id = b.league_id
    AND p.season_type = b.season_type
LEFT JOIN {{ ref('stg_player_scoring_breakdown') }} sb ON sb.player_id = b.player_id
    AND sb.season = b.season
    AND sb.league_id = b.league_id
    AND sb.season_type = b.season_type
LEFT JOIN season_possessions sp ON sp.player_id = b.player_id
    AND sp.season = b.season
    AND sp.league_id = b.league_id
    AND sp.season_type = b.season_type