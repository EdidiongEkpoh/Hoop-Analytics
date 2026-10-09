WITH by_team AS (
    SELECT *
    FROM {{ ref('stg_player_play_types') }}
)
, combined AS (
    SELECT player_id
        , season
        , league_id
        , season_type
        , play_type
        , type_grouping
        , (ARRAY_AGG(player_name ORDER BY possessions DESC))[1] AS player_name
        , COUNT(DISTINCT team_id) AS teams_played_for
        , SUM(possessions) AS possessions
        , SUM(pts) AS pts
        , SUM(fgm) AS fgm 
        , SUM(fga) AS fga 
        , SUM(efg_pct * fga) AS efg_weighted
        , SUM(tov_poss_pct * possessions) AS tov_possessions
        , SUM(ft_poss_pct * possessions) AS ft_possessions
        , SUM(score_poss_pct * possessions) AS scoring_possessions
    FROM by_team
    GROUP BY 1, 2, 3, 4, 5, 6
)
, league AS (
    SELECT season
        , league_id
        , season_type
        , play_type
        , type_grouping
        , SUM(pts) / NULLIF(SUM(possessions), 0) AS league_ppp
        , SUM(possessions) / NULLIF(SUM(SUM(possessions)) OVER (
            PARTITION BY season, league_id, season_type, type_grouping), 0) AS league_frequency
    FROM {{ ref('stg_team_play_types') }}
    GROUP BY 1, 2, 3, 4, 5
)
SELECT c.player_id
    , c.player_name
    , c.season
    , c.league_id
    , c.season_type
    , c.play_type
    , {{ play_type_label('c.play_type') }} AS play_type_label
    , c.type_grouping
    , c.teams_played_for
    , c.possessions
    , SUM(c.possessions) OVER (
        PARTITION BY c.player_id, c.season, c.season_type, c.league_id, c.type_grouping
    ) AS grouping_possessions
    , c.possessions / NULLIF(SUM(c.possessions) OVER (
        PARTITION BY c.player_id, c.season, c.season_type, c.league_id, c.type_grouping), 0) AS frequency
    , c.pts
    , c.pts / NULLIF(c.possessions, 0) AS ppp 
    , c.fgm / NULLIF(c.fga, 0) AS fg_pct 
    , c.efg_weighted / NULLIF(c.fga, 0) AS efg_pct
    , c.tov_possessions / NULLIF(c.possessions, 0) AS tov_freq
    , c.ft_possessions / NULLIF(c.possessions, 0) AS ft_freq
    , c.scoring_possessions / NULLIF(c.possessions, 0) AS score_freq
    , l.league_ppp
    , l.league_frequency
    , c.pts / NULLIF(c.possessions, 0) - l.league_ppp AS ppp_vs_league
FROM combined c 
LEFT JOIN league l ON l.season = c.season 
    AND l.league_id = c.league_id
    AND l.season_type = c.season_type
    AND l.play_type = c.play_type
    AND l.type_grouping = c.type_grouping