WITH stats AS (
    SELECT *
    FROM {{ ref('fct_team_opponent_stats_per_100') }}
)
SELECT team_id, season, league_id, season_type
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_pts_per_100) AS opp_ppg_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_fgm_per_100) AS opp_fgm_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_fga_per_100) AS opp_fga_per_100_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_fg3m_per_100) AS opp_fg3m_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_fg3a_per_100) AS opp_fg3a_per_100_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_ftm_per_100) AS opp_ftm_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_fta_per_100) AS opp_fta_per_100_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_oreb_per_100) AS opp_oreb_per_100percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_dreb_per_100) AS opp_dreb_per_100percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_reb_per_100) AS opp_reb_per_100percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_ast_per_100) AS opp_ast_per_100percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_stl_per_100) AS opp_stl_per_100percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_blk_per_100) AS opp_blk_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_tov_per_100) AS opp_tov_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY opp_pf_per_100) AS opp_pf_per_100_percentile
FROM stats