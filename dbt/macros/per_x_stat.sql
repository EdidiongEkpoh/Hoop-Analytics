{% macro per_x_stat(column, denominator, target) %}
    ROUND((({{ column }}::NUMERIC) / NULLIF({{ denominator }}, 0)) * {{ target }}, 2)
{% endmacro %}