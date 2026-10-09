{% set stats = ['fgm', 'fga', 'fg3m', 'fg3a', 'ftm', 'fta', 'oreb', 'dreb', 'reb', 'ast', 'stl', 'blk', 'tov',  'pf', 'pts'] %}

SELECT b.team_id
    , b.player_id
    , b.player_name
    , b.season
    , b.league_id
    , b.season_type
    , b.court_status
    , b.games_played
    , b.minutes
    , b.plus_minus
    {% for s in stats %}
    , b.{{ s }}
    , o.opp_{{ s }}
    {% endfor %}
    , b.fga + 0.44 * b.fta - b.oreb + b.tov AS team_est_poss
    , o.opp_fga + 0.44 * o.opp_fta - o.opp_oreb + o.opp_tov AS opp_est_poss
FROM {{ ref('stg_team_player_on_off') }} b 
LEFT JOIN {{ ref('stg_team_player_on_off_opponent') }} o ON o.team_id = b.team_id 
    AND o.player_id = b.player_id 
    AND o.court_status = b.court_status
    AND o.season = b.season 
    AND o.league_id = b.league_id
    AND o.season_type = b.season_type
