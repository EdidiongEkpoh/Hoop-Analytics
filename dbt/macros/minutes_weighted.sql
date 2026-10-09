{% macro minutes_weighted(rate_col, weight_col='minutes') -%}
    SUM({{ rate_col }} * {{ weight_col }})::NUMERIC
        / NULLIF(SUM(CASE WHEN {{ rate_col }} IS NOT NULL THEN {{ weight_col }} END), 0)
{%- endmacro %}