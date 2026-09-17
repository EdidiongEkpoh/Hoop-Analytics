WITH stats AS (
    SELECT *
    FROM {{ ref('fct_team_opponent_stats_per_game') }}
)
SELECT team_id, season, league_id, season_type
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_pts_per_game) AS opp_ppg_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_avg_fgm) AS opp_fgm_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_avg_fga) AS opp_fga_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_fg_pct) AS opp_fg_pct_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_avg_fg3m) AS opp_fg3m_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_avg_fg3a) AS opp_fg3a_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_fg3_pct) AS opp_fg3_pct_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_avg_ftm) AS opp_ftm_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_avg_fta) AS opp_fta_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_ft_pct) AS opp_ft_pct_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_oreb_per_game) AS opp_oreb_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_dreb_per_game) AS opp_dreb_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_reb_per_game) AS opp_reb_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_ast_per_game) AS opp_ast_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_stl_per_game) AS opp_stl_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_blk_per_game) AS opp_blk_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_tov_per_game) AS opp_tov_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_pf_per_game) AS opp_pf_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_offensive_rating) AS opp_offensive_rating_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_defensive_rating) AS opp_defensive_rating_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_net_rating) AS opp_net_rating_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_ast_pct) AS opp_ast_rt_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_ast_to_tov) AS opp_ast_to_tov_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_oreb_pct) AS opp_oreb_rt_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_dreb_pct) AS opp_dreb_rt_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_reb_pct) AS opp_reb_rt_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_tov_pct) AS opp_tov_rt_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_efg_pct) AS opp_efg_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_ts_pct) AS opp_ts_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_ftr) AS opp_ftr_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_fg3pr) AS opp_fg3pr_percentile
FROM stats