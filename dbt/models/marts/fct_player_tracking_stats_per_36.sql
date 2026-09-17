SELECT player_id, team_id, season, season_type, league_id, games_played, minutes, total_possessions
    , {{ per_x_stat('catch_shoot_fgm', 'minutes', 36) }} AS catch_shoot_fgm_per_36
    , {{ per_x_stat('catch_shoot_fga', 'minutes', 36) }} AS catch_shoot_fga_per_36
    , {{ per_x_stat('catch_shoot_pts', 'minutes', 36) }} AS catch_shoot_pts_per_36
    , {{ per_x_stat('catch_shoot_fg3m', 'minutes', 36) }} AS catch_shoot_fg3m_per_36
    , {{ per_x_stat('catch_shoot_fg3a', 'minutes', 36) }} AS catch_shoot_fg3a_per_36

    , {{ per_x_stat('drives', 'minutes', 36) }} AS drives_per_36
    , {{ per_x_stat('drive_fgm', 'minutes', 36) }} AS drive_fgm_per_36
    , {{ per_x_stat('drive_fga', 'minutes', 36) }} AS drive_fga_per_36
    , {{ per_x_stat('drive_pts', 'minutes', 36) }} AS drive_pts_per_36
    , {{ per_x_stat('drive_ast', 'minutes', 36) }} AS drive_ast_per_36
    , {{ per_x_stat('drive_tov', 'minutes', 36) }} AS drive_tov_per_36

    , {{ per_x_stat('post_touches', 'minutes', 36) }} AS post_touches_per_36
    , {{ per_x_stat('post_touch_fgm', 'minutes', 36) }} AS post_touch_fgm_per_36
    , {{ per_x_stat('post_touch_fga', 'minutes', 36) }} AS post_touch_fga_per_36
    , {{ per_x_stat('post_touch_pts', 'minutes', 36) }} AS post_touch_pts_per_36
    , {{ per_x_stat('post_touch_ast', 'minutes', 36) }} AS post_touch_ast_per_36
    , {{ per_x_stat('post_touch_tov', 'minutes', 36) }} AS post_touch_tov_per_36

    , {{ per_x_stat('pullup_fgm', 'minutes', 36) }} AS pullup_fgm_per_36
    , {{ per_x_stat('pullup_fga', 'minutes', 36) }} AS pullup_fga_per_36
    , {{ per_x_stat('pullup_fg3m', 'minutes', 36) }} AS pullup_fg3m_per_36
    , {{ per_x_stat('pullup_fg3a', 'minutes', 36) }} AS pullup_fg3a_per_36
    , {{ per_x_stat('pullup_pts', 'minutes', 36) }} AS pullup_pts_per_36
FROM {{ ref('fct_player_tracking_stats') }}