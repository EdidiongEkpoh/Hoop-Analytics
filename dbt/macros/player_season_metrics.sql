{% macro player_summed_columns() %}
    {{ return([
        'pts', 'reb', 'oreb', 'dreb', 'ast', 'stl', 'blk', 'tov', 'pf',
        'fgm', 'fga', 'fg2m', 'fg2a', 'fg3m', 'fg3a', 'ftm', 'fta',
        'minutes', 'possessions', 'plus_minus', 'opp_poss_on_court', 'opp_2pa_on_court'
    ])}}
{% endmacro %}

{% macro player_weighted_rates() %}
    {{ return ([
        'usage', 'assist_pct', 'oreb_pct', 'dreb_pct', 'reb_pct',
        'offensive_rating', 'defensive_rating', 'net_rating'
    ])}}

{% endmacro %}

{% macro player_scaled_stats() %}
    {{ return(['pts', 'oreb', 'dreb', 'reb', 'ast', 'stl', 'blk', 'tov', 'pf', 'plus_minus', 
                'fgm', 'fga', 'fg2m', 'fg2a', 'fg3m', 'fg3a', 'ftm', 'fta'])}}
{% endmacro %}

{% macro player_season_metrics() %}
    games_played
    , wins
    , total_minutes
    , total_minutes::NUMERIC / NULLIF(games_played, 0) AS minutes_per_game
    , total_possessions::NUMERIC / NULLIF(games_played, 0) AS possessions_per_game
    
    {% for s in player_scaled_stats() %}
    , total_{{ s }}
    , total_{{ s }}::NUMERIC / NULLIF(games_played, 0) AS {{ s }}_per_game
    , total_{{ s }}::NUMERIC * 36 / NULLIF(total_minutes, 0) AS {{ s }}_per_36
    , total_{{ s }}::NUMERIC * 75 / NULLIF(total_possessions, 0) AS {{ s }}_per_75
    , total_{{ s }}::NUMERIC * 100 / NULLIF(total_possessions, 0) AS {{ s }}_per_100
    {% endfor %}

    , total_fgm::NUMERIC / NULLIF(total_fga, 0) AS fg_pct
    , total_fg2m::NUMERIC / NULLIF(total_fg2a, 0) AS fg2_pct
    , total_fg3m::NUMERIC / NULLIF(total_fg3a, 0) AS fg3_pct
    , total_ftm::NUMERIC / NULLIF(total_fta, 0) AS ft_pct
    , total_fg3a::NUMERIC / NULLIF(total_fga, 0) AS fg3pr
    , total_fta::NUMERIC / NULLIF(total_fga, 0) AS ftr
    , (total_fgm + 0.5 * total_fg3m)::NUMERIC / NULLIF(total_fga, 0) AS efg_pct
    , total_pts::NUMERIC / NULLIF(2 * (total_fga + 0.44 * total_fta), 0) AS ts_pct

    , total_tov::NUMERIC / NULLIF(total_fga + 0.44 * total_fta + total_tov, 0) AS tov_pct
    , total_ast::NUMERIC / NULLIF(total_tov, 0) AS ast_to_tov
    , total_stl::NUMERIC / NULLIF(total_opp_poss_on_court, 0) AS stl_pct
    , total_blk::NUMERIC / NULLIF(total_opp_2pa_on_court, 0) AS blk_pct

    {% for r in player_weighted_rates() %}
    , wsum_{{ r }}::NUMERIC / NULLIF(wmin_{{ r }}, 0) AS {{ r }}
    {% endfor %}
{% endmacro %}

{% macro position_group(position_col) %}
    CASE UPPER(LEFT({{ position_col}}, 1))
        WHEN 'G' THEN 'Guard'
        WHEN 'F' THEN 'Forward'
        WHEN 'C' THEN 'Center'
    END
{% endmacro %}