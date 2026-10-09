SELECT game_id
    , game_event_id
    , player_id
    , player_name
    , team_id
    , team_name
    , season
    , league_id
    , season_type
    , game_date
    , quarter
    , minutes_remaining
    , seconds_remaining
    , event_type
    , action_type
    , shot_type
    , CASE WHEN shot_type = '3PT Field Goal' THEN 3 ELSE 2 END AS shot_value
    , shot_zone_basic
    , shot_zone_area
    , shot_zone_range
    , shot_distance
    , loc_x
    , loc_y
    , shot_made_flag
FROM {{ ref('stg_shot_chart_detail') }}