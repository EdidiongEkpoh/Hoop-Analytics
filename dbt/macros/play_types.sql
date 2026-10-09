{% macro play_type_label(col) %}
    CASE {{ col }}
        WHEN 'Transition' THEN 'Transition'
        WHEN 'Isolation' THEN 'Isolation'
        WHEN 'PRBallHandler' THEN 'P&R Ball Handler'
        WHEN 'PRRollman' THEN 'P&R Roll Man'
        WHEN 'Postup' THEN 'Post Up'
        WHEN 'Spotup' THEN 'Spot Up'
        WHEN 'Handoff' THEN 'Handoff'
        WHEN 'Cut' THEN 'Cut'
        WHEN 'OffScreen' THEN 'Off Screen'
        WHEN 'OffRebound' THEN 'Putbacks'
        WHEN 'Misc' THEN 'Misc'
        ELSE {{ col }}
    END
{% endmacro %}