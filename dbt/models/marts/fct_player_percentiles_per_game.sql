WITH stats AS (
    SELECT *
    FROM {{  ref('fct_player_season_summary')  }}
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
    , r.ppg_percentile
    , r.fgm_percentile
    , r.fga_percentile
    , r.fg_pct_percentile

    , r.fg3m_percentile
    , r.fg3a_percentile
    , r.fg3_pct_percentile

    , r.fg3pr_percentile

    , r.fg2m_percentile
    , r.fg2a_percentile
    , r.fg2_pct_percentile

    , r.ftm_percentile
    , r.fta_percentile
    , r.ft_pct_percentile
    , r.ftr_percentile

    , r.oreb_percentile
    , r.dreb_percentile
    , r.reb_percentile
    , r.ast_percentile

    , r.stl_pct_percentile
    , r.blk_pct_percentile
    , r.stk_percentile
    , r.tov_percentile
    , r.pf_percentile

    , r.usage_percentile
    , r.efg_percentile
    , r.ts_percentile
    , r.stl_percentile
    , r.blk_percentile

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