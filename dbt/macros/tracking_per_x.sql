{% macro tracking_per_x(denominator, factor, suffix) %}
    {% set stats = [
        'catch_shoot_fgm', 'catch_shoot_fga', 'catch_shoot_fg3m', 'catch_shoot_fg3a', 'catch_shoot_efg', 'catch_shoot_pts',
        'drives', 'drive_fgm', 'drive_fga', 'drive_ftm', 'drive_fta', 'drive_pts', 'drive_ast', 'drive_tov', 'drive_pf',
        'post_touches', 'post_touch_fgm', 'post_touch_fga', 'post_touch_ftm', 'post_touch_fta', 'post_touch_pts', 'post_touch_ast', 'post_touch_tov', 'post_touch_fouls',
        'pullup_fgm', 'pullup_fga', 'pullup_fg3m', 'pullup_fg3a', 'pullup_efg_pct', 'pullup_pts'
    ] %}
    SELECT player_id, team_id, season, league_id, season_type, games_played, minutes, total_possessions
    {% for s in stats %}
        , {{ s }}::NUMERIC * {{ factor }} / NULLIF({{ denominator }}, 0) AS {{ s }}_{{ suffix }}
    {% endfor %}
    FROM {{ ref('fct_player_tracking_stats') }}
{% endmacro %}