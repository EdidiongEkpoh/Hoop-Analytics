WITH player_zones AS (
    SELECT player_id
        , team_id
        , season
        , league_id
        , season_type
        , shot_zone_basic
        , shot_zone_area
        , shot_zone_range
        , COUNT(*) AS fga
        , SUM(shot_made_flag) AS fgm
        , AVG(shot_made_flag::FLOAT) AS fg_pct 
    FROM {{  ref('stg_shot_chart_detail')   }}
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
)
SELECT pz.*
    , la.fg_pct AS league_avg_fg_pct
    , pz.fg_pct - la.fg_pct AS fg_pct_vs_league
FROM player_zones pz
LEFT JOIN {{  ref('stg_shot_zone_league_averages')  }} la ON la.season = pz.season
    AND la.league_id = pz.league_id
    AND la.season_type = pz.season_type
    AND la.shot_zone_basic = pz.shot_zone_basic
    AND la.shot_zone_area = pz.shot_zone_area
    AND la.shot_zone_range = pz.shot_zone_range