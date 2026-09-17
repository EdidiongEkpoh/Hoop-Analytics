SELECT player_id, team_id, season, season_type, league_id, games_played, minutes, total_possessions
    , {{ per_x_stat('catch_shoot_fgm', 'total_possessions', 100) }} AS catch_shoot_fgm_per_100
    , {{ per_x_stat('catch_shoot_fga', 'total_possessions', 100) }} AS catch_shoot_fga_per_100
    , {{ per_x_stat('catch_shoot_pts', 'total_possessions', 100) }} AS catch_shoot_pts_per_100
    , {{ per_x_stat('catch_shoot_fg3m', 'total_possessions', 100) }} AS catch_shoot_fg3m_per_100
    , {{ per_x_stat('catch_shoot_fg3a', 'total_possessions', 100) }} AS catch_shoot_fg3a_per_100

    , {{ per_x_stat('drives', 'total_possessions', 100) }} AS drives_per_100
    , {{ per_x_stat('drive_fgm', 'total_possessions', 100) }} AS drive_fgm_per_100
    , {{ per_x_stat('drive_fga', 'total_possessions', 100) }} AS drive_fga_per_100
    , {{ per_x_stat('drive_pts', 'total_possessions', 100) }} AS drive_pts_per_100
    , {{ per_x_stat('drive_ast', 'total_possessions', 100) }} AS drive_ast_per_100
    , {{ per_x_stat('drive_tov', 'total_possessions', 100) }} AS drive_tov_per_100

    , {{ per_x_stat('post_touches', 'total_possessions', 100) }} AS post_touches_per_100
    , {{ per_x_stat('post_touch_fgm', 'total_possessions', 100) }} AS post_touch_fgm_per_100
    , {{ per_x_stat('post_touch_fga', 'total_possessions', 100) }} AS post_touch_fga_per_100
    , {{ per_x_stat('post_touch_pts', 'total_possessions', 100) }} AS post_touch_pts_per_100
    , {{ per_x_stat('post_touch_ast', 'total_possessions', 100) }} AS post_touch_ast_per_100
    , {{ per_x_stat('post_touch_tov', 'total_possessions', 100) }} AS post_touch_tov_per_100

    , {{ per_x_stat('pullup_fgm', 'total_possessions', 100) }} AS pullup_fgm_per_100
    , {{ per_x_stat('pullup_fga', 'total_possessions', 100) }} AS pullup_fga_per_100
    , {{ per_x_stat('pullup_fg3m', 'total_possessions', 100) }} AS pullup_fg3m_per_100
    , {{ per_x_stat('pullup_fg3a', 'total_possessions', 100) }} AS pullup_fg3a_per_100
    , {{ per_x_stat('pullup_pts', 'total_possessions', 100) }} AS pullup_pts_per_100
FROM {{ ref('fct_player_tracking_stats') }}