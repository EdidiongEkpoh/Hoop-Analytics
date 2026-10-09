WITH league AS (
    SELECT season
        , league_id
        , season_type
        , COUNT(*) AS teams
        , SUM(games_played) AS team_games
        , SUM(total_minutes) AS total_minutes
        , SUM(total_possessions) AS total_possessions
        , SUM(opp_total_possessions) AS opp_total_possessions
        , SUM(total_pts) AS total_pts
        , SUM(total_fgm) AS total_fgm
        , SUM(total_fga) AS total_fga
        , SUM(total_fg3m) AS total_fg3m
        , SUM(total_fg3a) AS total_fg3a
        , SUM(total_ftm) AS total_ftm
        , SUM(total_fta) AS total_fta
        , SUM(total_oreb) AS total_oreb
        , SUM(total_dreb) AS total_dreb
        , SUM(total_tov) AS total_tov
    FROM {{ ref('int_team_season_stats') }}
    GROUP BY 1, 2, 3
)
SELECT season
    , league_id
    , season_type
    , teams
    , team_games
    , total_pts::NUMERIC / NULLIF(team_games, 0) AS pts_per_game
    , 48 * (total_possessions + opp_total_possessions)::NUMERIC
        / NULLIF(2 * (total_minutes::NUMERIC / 5), 0) AS pace
    , 100.0 * total_pts / NULLIF(total_possessions, 0) AS offensive_rating
    , total_fgm::NUMERIC / NULLIF(total_fga, 0) AS fg_pct
    , total_fg3m::NUMERIC / NULLIF(total_fg3a, 0) AS fg3_pct
    , total_ftm::NUMERIC / NULLIF(total_fta, 0) AS ft_pct
    , total_fg3a::NUMERIC / NULLIF(total_fga, 0) AS fg3pr
    , total_fta::NUMERIC / NULLIF(total_fga, 0) AS ftr
    , (total_fgm + 0.5 * total_fg3m)::NUMERIC / NULLIF(total_fga, 0) AS efg_pct
    , total_pts::NUMERIC / NULLIF(2 * (total_fga + 0.44 * total_fta), 0) AS ts_pct
    , total_tov::NUMERIC / NULLIF(total_fga + 0.44 * total_fta + total_tov, 0) AS tov_pct
    , total_oreb::NUMERIC / NULLIF(total_oreb + total_dreb, 0) AS oreb_pct
FROM league