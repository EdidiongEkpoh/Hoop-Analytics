WITH stats AS (
    SELECT *
    FROM {{  ref('fct_player_stats_per_36')  }}
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
, ranked AS (
    SELECT player_id
        , team_id
        , season
        , league_id
        , season_type
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY pts_per_36) AS pts_per_36_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fgm_per_36) AS fgm_per_36_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fga_per_36) AS fga_per_36_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg_pct) AS fg_pct_percentile

        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg3m_per_36) AS fg3m_per_36_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg3a_per_36) AS fg3a_per_36_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg3_pct) AS fg3_pct_percentile

        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg3pr) AS fg3pr_percentile

        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg2m_per_36) AS fg2m_per_36_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg2a_per_36) AS fg2a_per_36_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg2_pct) AS fg2_pct_percentile

        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY ftm_per_36) AS ftm_per_36_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fta_per_36) AS fta_per_36_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY ft_pct) AS ft_pct_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY ftr) AS ftr_percentile

        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY oreb_per_36) AS oreb_per_36_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY dreb_per_36) AS dreb_per_36_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY reb_per_36) AS reb_per_36_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY ast_per_36) AS ast_per_36_percentile

        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY stl_per_36) AS stl_per_36_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY blk_per_36) AS blk_per_36_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY stk_per_36) AS stk_per_36_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY tov_per_36) AS tov_per_36_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY pf_per_36) AS pf_per_36_percentile

        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY usage) AS usage_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY efg_pct) AS efg_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY ts_pct) AS ts_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY stl_pct) AS stl_pct_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY blk_pct) AS blk_pct_percentile

        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY assist_pct) AS ast_pct_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY ast_to_tov) AS ast_to_tov_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY oreb_pct) AS oreb_pct_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY dreb_pct) AS dreb_pct_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY reb_pct) AS reb_pct_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY tov_pct) AS tov_pct_percentile

        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY offensive_rating) AS off_rating_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY defensive_rating) AS def_rating_percentile
        , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY net_rating) AS net_rating_percentile
    FROM eligible
)
SELECT s.player_id, s.team_id, s.season, s.league_id, s.season_type, s.games_played
    , r.pts_per_36_percentile
    , r.fgm_per_36_percentile
    , r.fga_per_36_percentile
    , r.fg_pct_percentile

    , r.fg3m_per_36_percentile
    , r.fg3a_per_36_percentile
    , r.fg3_pct_percentile

    , r.fg3pr_percentile

    , r.fg2m_per_36_percentile
    , r.fg2a_per_36_percentile
    , r.fg2_pct_percentile

    , r.ftm_per_36_percentile
    , r.fta_per_36_percentile
    , r.ft_pct_percentile
    , r.ftr_percentile

    , r.oreb_per_36_percentile
    , r.dreb_per_36_percentile
    , r.reb_per_36_percentile
    , r.ast_per_36_percentile

    , r.stl_per_36_percentile
    , r.blk_per_36_percentile
    , r.stk_per_36_percentile
    , r.tov_per_36_percentile
    , r.pf_per_36_percentile

    , r.usage_percentile
    , r.efg_percentile
    , r.ts_percentile
    , r.stl_pct_percentile
    , r.blk_pct_percentile

    , r.ast_pct_percentile
    , r.ast_to_tov_percentile
    , r.oreb_pct_percentile
    , r.dreb_pct_percentile
    , r.reb_pct_percentile
    , r.tov_pct_percentile

    , r.off_rating_percentile
    , r.def_rating_percentile
    , r.net_rating_percentile
FROM stats s
LEFT JOIN ranked r ON r.player_id = s.player_id AND r.team_id = s.team_id
    AND r.season = s.season AND r.league_id = s.league_id AND r.season_type = s.season_type