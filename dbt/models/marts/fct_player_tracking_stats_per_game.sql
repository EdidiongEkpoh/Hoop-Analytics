SELECT player_id, team_id, season, season_type, league_id, games_played, minutes, total_possessions
    , 1.0 * catch_shoot_fgm / NULLIF(games_played, 0) AS catch_shoot_fgm_per_game
    , 1.0 * catch_shoot_fga / NULLIF(games_played, 0) AS catch_shoot_fga_per_game
    , 1.0 * catch_shoot_pts / NULLIF(games_played, 0) AS catch_shoot_pts_per_game
    , 1.0 * catch_shoot_fg3m / NULLIF(games_played, 0) AS catch_shoot_fg3m_per_game
    , 1.0 * catch_shoot_fg3a / NULLIF(games_played, 0) AS catch_shoot_fg3a_per_game

    , 1.0 * drives / NULLIF(games_played, 0) AS drives_per_game
    , 1.0 * drive_fgm / NULLIF(games_played, 0) AS drive_fgm_per_game
    , 1.0 * drive_fga / NULLIF(games_played, 0) AS drive_fga_per_game
    , 1.0 * drive_pts / NULLIF(games_played, 0) AS drive_pts_per_game
    , 1.0 * drive_ast / NULLIF(games_played, 0) AS drive_ast_per_game
    , 1.0 * drive_tov / NULLIF(games_played, 0) AS drive_tov_per_game

    , 1.0 * post_touches / NULLIF(games_played, 0) AS post_touches_per_game
    , 1.0 * post_touch_fgm / NULLIF(games_played, 0) AS post_touch_fgm_per_game
    , 1.0 * post_touch_fga / NULLIF(games_played, 0) AS post_touch_fga_per_game
    , 1.0 * post_touch_pts / NULLIF(games_played, 0) AS post_touch_pts_per_game
    , 1.0 * post_touch_ast / NULLIF(games_played, 0) AS post_touch_ast_per_game
    , 1.0 * post_touch_tov / NULLIF(games_played, 0) AS post_touch_tov_per_game

    , 1.0 * pullup_fgm / NULLIF(games_played, 0) AS pullup_fgm_per_game
    , 1.0 * pullup_fga / NULLIF(games_played, 0) AS pullup_fga_per_game
    , 1.0 * pullup_fg3m / NULLIF(games_played, 0) AS pullup_fg3m_per_game
    , 1.0 * pullup_fg3a / NULLIF(games_played, 0) AS pullup_fg3a_per_game
    , 1.0 * pullup_pts / NULLIF(games_played, 0) AS pullup_pts_per_game
FROM {{ ref('fct_player_tracking_stats') }}