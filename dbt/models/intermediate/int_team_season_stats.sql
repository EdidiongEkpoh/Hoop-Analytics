{{ config(materialized='table') }}

{% set team_cols = [
    'pts', 'fgm', 'fga', 'fg2m', 'fg2a', 'fg3m', 'fg3a', 'ftm', 'fta', 'oreb', 'dreb', 'reb', 'ast', 'stl', 'blk', 'tov', 'pf'
    , 'possessions', 'minutes'
] %}

{% set opponent_cols = [
    'pts', 'fgm', 'fga','fg3m', 'fg3a', 'ftm', 'fta', 'oreb', 'dreb', 'reb', 'ast', 'stl', 'blk', 'tov', 'pf'
    , 'possessions'
] %}

SELECT team_id  
    , season
    , league_id 
    , season_type
    , (ARRAY_AGG(team_name ORDER BY game_date DESC))[1] AS team_name
    , COUNT(*) AS games_played 
    , SUM(win_flag) AS wins
    , SUM(loss_flag) AS losses
    , COUNT(*) FILTER (WHERE home_away = 'Home') AS home_games
    , SUM(win_flag) FILTER (WHERE home_away = 'Home') AS home_wins
    , COUNT(*) FILTER (WHERE home_away = 'Away') AS away_games
    , SUM(win_flag) FILTER (WHERE home_away = 'Awat') AS away_wins

    {% for c in team_cols %}
    , SUM({{ c }}) AS total_{{ c }}
    {% endfor %}

    {% for c in opponent_cols %}
    , SUM(opponent_{{ c }}) AS opp_total_{{ c }}
    {% endfor %}
FROM {{ ref('int_team_games_with_opponent')  }}
GROUP BY 1, 2, 3, 4