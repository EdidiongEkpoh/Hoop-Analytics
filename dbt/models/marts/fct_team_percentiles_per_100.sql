WITH stats AS (
    SELECT *
    FROM {{  ref('fct_team_stats_per_100')  }}
)
SELECT team_id, season, league_id, season_type
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY pts_per_100) AS pts_per_100_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fgm_per_100) AS fgm_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fga_per_100) AS fga_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg_pct) AS fg_pct_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg3m_per_100) AS fg3m_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg3a_per_100) AS fg3a_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg3_pct) AS fg3_pct_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg3pr) AS fg3pr_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg2m_per_100) AS fg2m_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg2a_per_100) AS fg2a_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg2_pct) AS fg2_pct_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY ftm_per_100) AS ftm_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fta_per_100) AS fta_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY ft_pct) AS ft_pct_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY ftr) AS ftr_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY oreb_per_100) AS oreb_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY dreb_per_100) AS dreb_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY reb_per_100) AS reb_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY ast_per_100) AS ast_per_100_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY stl_per_100) AS stl_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY blk_per_100) AS blk_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY stk_per_100) AS stk_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY tov_per_100) AS tov_per_100_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY pf_per_100) AS pf_per_100_percentile
FROM stats