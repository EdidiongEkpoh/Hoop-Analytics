WITH stats AS (
    SELECT *
    FROM {{  ref('fct_player_tracking_stats')  }}
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

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY catch_shoot_pts) AS catch_shoot_pts_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY catch_shoot_fgm) AS catch_shoot_fgm_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY catch_shoot_fga) AS catch_shoot_fga_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY catch_shoot_fg3m) AS catch_shoot_fg3m_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY catch_shoot_fg3a) AS catch_shoot_fg3a_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY pullup_pts) AS pullup_pts_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY pullup_fgm) AS pullup_fgm_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY pullup_fga) AS pullup_fga_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY pullup_fg3m) AS pullup_fg3m_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY pullup_fg3a) AS pullup_fg3a_percentile
    

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY drives) AS drives_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY drive_pts) AS drive_pts_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY drive_fgm) AS drive_fgm_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY drive_fga) AS drive_fga_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY drive_ast) AS drive_ast_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY drive_tov) AS drive_tov_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY post_touches) AS post_touches_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY post_touch_pts) AS post_touch_pts_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY post_touch_fgm) AS post_touch_fgm_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY post_touch_fga) AS post_touch_fga_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY post_touch_ast) AS post_touch_ast_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY post_touch_tov) AS post_touch_tov_percentile
FROM eligible