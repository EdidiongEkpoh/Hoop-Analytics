SELECT team_id
    , player_id
    , season
    , league_id
    , player_name
    , jersey_number
    , position
    , height
    , weight
    , birthdate
    , age
    , player_exp
    , school
    , how_acquired
FROM {{ ref('stg_team_rosters') }}