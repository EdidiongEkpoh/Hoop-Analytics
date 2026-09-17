WITH stats AS (
    SELECT *
    FROM {{  ref('fct_player_tracking_stats_per_100')  }}
)
, eligible AS (
    SELECT s.*
    FROM stats s
    JOIN {{  ref('int_player_eligibility')  }} e ON e.player_id = s.player_id 
        AND e.season = s.season
        AND e.season_type = s.season_type 
        AND e.league_id = s.league_id
    WHERE e.meets_min_games_threshold = TRUE 
)
SELECT player_id, team_id, season, league_id, season_type

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY catch_shoot_pts_per_100) AS catch_shoot_pts_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY catch_shoot_fgm_per_100) AS catch_shoot_fgm_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY catch_shoot_fga_per_100) AS catch_shoot_fga_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY catch_shoot_fg3m_per_100) AS catch_shoot_fg3m_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY catch_shoot_fg3a_per_100) AS catch_shoot_fg3a_per_100_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY pullup_pts_per_100) AS pullup_pts_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY pullup_fgm_per_100) AS pullup_fgm_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY pullup_fga_per_100) AS pullup_fga_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY pullup_fg3m_per_100) AS pullup_fg3m_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY pullup_fg3a_per_100) AS pullup_fg3a_100_percentile
    

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY drives_per_100) AS drives_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY drive_pts_per_100) AS drive_pts_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY drive_fgm_per_100) AS drive_fgm_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY drive_fga_per_100) AS drive_fga_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY drive_ast_per_100) AS drive_ast_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY drive_tov_per_100) AS drive_tov_100_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY post_touches_per_100) AS post_touches_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY post_touch_pts_per_100) AS post_touch_pts_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY post_touch_fgm_per_100) AS post_touch_fgm_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY post_touch_fga_per_100) AS post_touch_fga_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY post_touch_ast_per_100) AS post_touch_ast_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY post_touch_tov_per_100) AS post_touch_tov_per_100_percentile
FROM eligible