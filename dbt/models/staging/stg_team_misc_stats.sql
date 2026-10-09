SELECT CAST("TEAM_ID" AS VARCHAR) AS team_id
    , CAST("TEAM_NAME" AS VARCHAR) AS team_name
    , CAST(_extract_season AS VARCHAR) AS season
    , CAST(_extract_league_id AS VARCHAR) AS league_id
    , CAST(_extract_season_type AS VARCHAR) AS season_type
    , CAST("GP" AS INTEGER) AS games_played
    , CAST("PTS_OFF_TOV" AS NUMERIC) AS pts_off_tov
    , CAST("PTS_2ND_CHANCE" AS NUMERIC) AS pts_2nd_chance
    , CAST("PTS_FB" AS NUMERIC) AS pts_fast_break
    , CAST("PTS_PAINT" AS NUMERIC) AS pts_paint
    , CAST("OPP_PTS_OFF_TOV" AS NUMERIC) AS opp_pts_off_tov
    , CAST("OPP_PTS_2ND_CHANCE" AS NUMERIC) AS opp_pts_2nd_chance
    , CAST("OPP_PTS_FB" AS NUMERIC) AS opp_pts_fast_break
    , CAST("OPP_PTS_PAINT" AS NUMERIC) AS opp_pts_paint
    
FROM {{ source('raw_nba', 'team_misc_stats') }}