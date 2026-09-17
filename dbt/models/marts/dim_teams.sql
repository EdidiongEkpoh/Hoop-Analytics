SELECT t.id AS team_id
    , t.full_name 
    , t.abbreviation 
    , t.city 
    , t.state 
FROM {{ ref('stg_teams')  }} t
