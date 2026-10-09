{% set categories = {
    'Overall': 'overall', '3 Pointers': 'fg3', '2 Pointers': 'fg2', 'Less Than 6Ft': 'rim', 
    'Less Than 10Ft': 'lt_10ft', 'Greater Than 15Ft': 'gt_15ft'
} %}
{% set hustle_per_36 = [
    'contested_shots', 'contested_shots_2pt', 'contested_shots_3pt', 'deflections', 'charges_drawn',
    'screen_assists', 'screen_assist_pts', 'loose_balls_recovered', 'boxouts'
] %}

WITH by_category AS (
    SELECT player_id
        , season 
        , league_id
        , season_type
        , defense_category
        , MAX(player_name) AS player_name
        , MAX(team_id) AS team_id 
        , SUM(d_fgm) AS d_fgm
        , SUM(d_fga) AS d_fga
        , SUM(normal_fg_pct * d_fga) / NULLIF(SUM(d_fga), 0) AS normal_fg_pct
    FROM {{ ref('stg_player_defense_dashboard') }}
    GROUP BY 1, 2, 3, 4, 5
)
, defend AS (
    SELECT player_id
        , season 
        , league_id
        , season_type
        , MAX(player_name) AS player_name
        , MAX(team_id) AS team_id
        {% for category, prefix in categories.items() %}
        , MAX(CASE WHEN defense_category = '{{ category }}' THEN d_fga END) AS {{ prefix }}_d_fga
        , MAX(CASE WHEN defense_category = '{{ category }}' THEN d_fgm / NULLIF(d_fga, 0) END) AS {{ prefix }}_d_fg_pct
        , MAX(CASE WHEN defense_category = '{{ category }}' THEN normal_fg_pct END) AS {{ prefix }}_normal_fg_pct
        , MAX(CASE WHEN defense_category = '{{ category }}' THEN d_fgm / NULLIF(d_fga, 0) - normal_fg_pct END) AS {{ prefix }}_fg_pct_diff
        {% endfor %}
    FROM by_category
    GROUP BY 1, 2, 3, 4
)
, hustle AS (
    SELECT *
    FROM {{ ref('stg_player_hustle_stats') }}
)
SELECT COALESCE(h.player_id, d.player_id) AS player_id
    , COALESCE(h.player_name, d.player_name) AS player_name
    , COALESCE(h.team_id, d.team_id) AS last_team_id
    , COALESCE(h.season, d.season) AS season
    , COALESCE(h.season_type, d.season_type) AS season_type
    , COALESCE(h.league_id, d.league_id) AS league_id
    , h.games_played
    , h.minutes
    {% for s in hustle_per_36 %}
    , h.{{ s }}
    , h.{{ s }} * 36 / NULLIF(h.minutes, 0) AS {{ s }}_per_36
    {% endfor %}
    , h.off_loose_balls_recovered
    , h.def_loose_balls_recovered
    , h.off_boxouts
    , h.def_boxouts
    , h.boxout_team_rebs
    , h.boxout_player_rebs
    {% for prefix in categories.values() %}
    , d.{{ prefix }}_d_fga
    , d.{{ prefix }}_d_fg_pct
    , d.{{ prefix }}_normal_fg_pct
    , d.{{ prefix }}_fg_pct_diff
    {% endfor %}
FROM hustle h 
FULL OUTER JOIN defend d ON d.player_id = h.player_id
    AND d.season = h.season 
    AND d.league_id = h.league_id
    AND d.season_type = h.season_type