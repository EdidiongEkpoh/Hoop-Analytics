WITH t AS (
    SELECT *    
        , SUM(possessions) OVER (
            PARTITION BY team_id, season, league_id, season_type, type_grouping) AS grouping_possessions
    FROM {{ ref('stg_team_play_types') }}
)
, league AS (
    SELECT season
        , league_id
        , season_type
        , play_type
        , type_grouping
        , SUM(pts) / NULLIF(SUM(possessions), 0) AS league_ppp
        , SUM(possessions) / NULLIF(SUM(grouping_possessions), 0) AS league_frequency
    FROM t
    GROUP BY 1, 2, 3, 4, 5
)
SELECT t.team_id
    , t.team_name 
    , t.season
    , t.season_type
    , t.league_id
    , t.play_type
    , {{ play_type_label('t.play_type') }} AS play_type_label
    , t.type_grouping
    , t.possessions
    , t.grouping_possessions
    , t.possessions / NULLIF(t.grouping_possessions, 0) AS frequency
    , t.pts
    , t.pts / NULLIF(t.possessions, 0) AS ppp
    , t.efg_pct
    , t.tov_poss_pct AS tov_freq
    , t.score_poss_pct AS score_freq
    , l.league_ppp
    , l.league_frequency
    , t.pts / NULLIF(t.possessions, 0) - l.league_ppp AS ppp_vs_league
    , RANK() OVER (
        PARTITION BY t.season, t.league_id, t.season_type, t.play_type, t.type_grouping
        ORDER BY CASE WHEN t.type_grouping = 'offensive'
                      THEN -(t.pts / NULLIF(t.possessions, 0))
                      ELSE t.pts / NULLIF(t.possessions, 0) END
    ) AS ppp_rank
FROM t 
LEFT JOIN league l ON l.season = t.season
    AND l.league_id = t.league_id
    AND l.season_type = t.season_type
    AND l.play_type = t.play_type
    AND l.type_grouping = t.type_grouping