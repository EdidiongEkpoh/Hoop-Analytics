SELECT gl.*
    , gl.fg2m::NUMERIC / NULLIF(gl.fg2a, 0) AS fg2_pct
FROM {{ ref('int_player_game_logs')  }} gl