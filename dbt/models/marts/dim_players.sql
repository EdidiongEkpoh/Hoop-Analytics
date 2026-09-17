WITH latest_team AS (
    SELECT player_id
        , team_id 
        , team_name
        , ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY game_date DESC) AS rn
    FROM {{ ref('int_player_game_logs')  }}
)
, latest_player_info AS (
    SELECT *
        , ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY season DESC) AS rn
    FROM {{ ref('stg_player_info')  }}
)
SELECT p.id AS player_id 
    , p.full_name AS player_name 
    , i.position
    , i.height
    , i.weight 
    , i.birthdate 
    , i.school
    , i.country 
    , i.draft_year 
    , i.draft_round
    , i.draft_number 
    , lt.team_id AS current_team_id 
    , lt.team_name AS current_team_name
FROM {{ ref('stg_players')  }} p 
LEFT JOIN latest_player_info i ON i.player_id = p.id AND i.rn = 1
LEFT JOIN latest_team lt ON lt.player_id = p.id AND lt.rn = 1