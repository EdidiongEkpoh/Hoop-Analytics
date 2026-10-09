WITH player_ids AS (
    SELECT id AS player_id
    FROM {{ ref('stg_players') }}
    UNION 
    SELECT player_id
    FROM {{ ref('stg_player_info') }}
)
, latest_player_info AS (
    SELECT * 
        , ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY season DESC) AS rn 
    FROM {{ ref('stg_player_info') }}
)
, latest_team AS (
    SELECT player_id 
        , team_id
        , team_name 
        , ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY game_date DESC) AS rn
    FROM {{ ref('int_player_game_logs') }}
)
, overrides AS (
    SELECT *
    FROM {{ ref('player_info_overrides') }}
)
SELECT p.player_id 
    , COALESCE(i.full_name, sp.full_name) AS player_name
    , COALESCE(ov.position, i.position) AS position
    , COALESCE(ov.height, i.height) AS height
    , COALESCE(ov.weight, i.weight) AS weight
    , COALESCE(ov.birthdate, i.birthdate) AS birthdate
    , COALESCE(ov.school, i.school) AS school
    , COALESCE(ov.country, i.country) AS country

    , COALESCE(ov.draft_year, i.draft_year) AS draft_year
    , COALESCE(ov.draft_round, i.draft_round) AS draft_round
    , COALESCE(ov.draft_number, i.draft_number) AS draft_number
    , lt.team_id AS current_team_id
    , lt.team_name AS current_team_name
FROM player_ids p 
LEFT JOIN overrides ov ON ov.player_id = p.player_id
LEFT JOIN {{ ref('stg_players') }} sp ON sp.id = p.player_id
LEFT JOIN latest_player_info i ON i.player_id = p.player_id 
    AND i.rn = 1 
LEFT JOIN latest_team lt ON lt.player_id = p.player_id
    AND lt.rn = 1
