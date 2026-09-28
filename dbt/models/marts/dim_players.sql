WITH all_players AS (
    SELECT id AS player_id
        , full_name AS player_name
    FROM staging_staging.stg_players
    UNION
    SELECT player_id
        , full_name 
    FROM staging_staging.stg_player_info
)
, latest_player_info AS (
    SELECT * 
        , ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY season DESC) AS rn 
    FROM staging_staging.stg_player_info
)
, latest_team AS (
    SELECT player_id 
        , team_id
        , team_name 
        , ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY game_date DESC) AS rn
    FROM staging_staging.int_player_game_logs
)
, overrides AS (
    SELECT *
    FROM {{ ref('player_info_overrides') }}
)
SELECT ap.player_id 
    , ap.player_name
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
FROM all_players ap 
LEFT JOIN overrides ov ON ov.player_id = ap.player_id
LEFT JOIN latest_player_info i ON i.player_id = ap.player_id 
    AND i.rn = 1 
LEFT JOIN latest_team lt ON lt.player_id = ap.player_id
    AND lt.rn = 1
WHERE ap.player_name NOT IN ('Bobby Portis', 'Boban Marjanovic', 'Monté Morris'
    , 'Terrence Shannon Jr', 'Jonas Valanciunas', 'Bojan Bogdanović',
     'Davis Bertans', 'Dante Exum', 'Dario Saric')