WITH stats AS (
    SELECT *
    FROM {{  ref('fct_team_season_summary')  }}
)
SELECT team_id, season, league_id, season_type
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY pts_per_game) AS ppg_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY avg_fgm) AS fgm_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY avg_fga) AS fga_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg_pct) AS fg_pct_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY avg_fg3m) AS fg3m_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY avg_fg3a) AS fg3a_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg3_pct) AS fg3_pct_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg3pr) AS fg3pr_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY avg_fg2m) AS fg2m_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY avg_fg2a) AS fg2a_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY fg2_pct) AS fg2_pct_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY avg_ftm) AS ftm_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY avg_fta) AS fta_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY ft_pct) AS ft_pct_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY ftr) AS ftr_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY orebs_per_game) AS oreb_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY drebs_per_game) AS dreb_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY rebs_per_game) AS reb_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY asts_per_game) AS ast_percentile

    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY stls_per_game) AS stl_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY blks_per_game) AS blk_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY stks_per_game) AS stk_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY tovs_per_game) AS tov_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY pf_per_game) AS pf_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY offensive_rating) AS offensive_rating_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY defensive_rating) AS defensive_rating_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY net_rating) AS net_rating_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY assist_pct) AS ast_rt_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY ast_to_tov) AS ato_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY oreb_pct) AS oreb_rt_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY dreb_pct) AS dreb_rt_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY reb_pct) AS reb_rt_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY tov_pct) AS tov_rt_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY efg_pct) AS efg_percentile
    , PERCENT_RANK() OVER (PARTITION BY season, league_id, season_type ORDER BY ts_pct) AS ts_percentile
FROM stats