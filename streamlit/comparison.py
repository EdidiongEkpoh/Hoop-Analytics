import streamlit as st
from db import run_query, available_seasons
from ui import inject_css, comparison_row_html

inject_css()
st.markdown(
    '''
    <div style="display:flex; justify-content:center; align-items:center;  margin-bottom:1rem;">
        <h1 style="margin:0;">Comparison</h1>
    </div>
    ''', unsafe_allow_html=True
)

mode = st.radio("", ["Teams", "Players"], horizontal=True)

if mode == "Teams":
    col_left, col_right = st.columns(2)
    def team_filters(col, side_key):
        with col:
            season = st.selectbox("Season", available_seasons(), key=f"season_{side_key}")
            season_type = st.selectbox("Season Type", ["Regular Season", "Playoffs"], key=f"type_{side_key}")
            if season_type == 'Playoffs':
                teams = run_query(
                    '''
                    SELECT DISTINCT team_id
                        , team_name
                    FROM staging_marts.dim_standings ds
                    JOIN staging_marts.fct_team_games tg ON tg.team_id = ds.team_id
                        AND tg.season = ds.season
                        AND tg.league_id = ds.league_id
                        AND tg.season_type = 'Playoffs'
                    WHERE ds.season = :season
                        AND ds.league_id = '00'
                    '''
                    , {'season': season}
                )
            else:
                teams = run_query(
                    '''
                    SELECT DISTINCT team_id
                        , team_name
                    FROM staging_marts.dim_standings
                    WHERE season = :season
                        AND league_id = '00'
                    '''
                    , {'season': season}
                )
            team_name = st.selectbox("Teams", teams['team_name'], key=f"team_{side_key}")
            team_id = teams.loc[teams['team_name'] == team_name, "team_id"].iloc[0]
        return season, season_type, team_id, team_name

    season_L, type_L, team_id_L, team_name_L = team_filters(col_left, "L")
    season_R, type_R, team_id_R, team_name_R = team_filters(col_right, "R")

    def get_team_data(team_id, season, season_type):
        core = run_query(
            '''
            SELECT ts.offensive_rating, ts.defensive_rating, ts.net_rating, ts.pace
                , ts.efg_pct, ts.tov_pct, ts.oreb_pct, ts.dreb_pct, ts.ftr, os.opp_efg_pct
                , os.opp_tov_pct, os.opp_ftr
            FROM staging_marts.fct_team_stats_per_100 ts
            LEFT JOIN staging_marts.fct_team_opponent_stats_per_100 os ON os.team_id = ts.team_id
                AND os.league_id = ts.league_id
                AND os.season = ts.season
                AND os.season_type = ts.season_type
            WHERE ts.team_id = :team_id
                AND ts.season = :season
                AND ts.league_id = '00'
                AND ts.season_type = :season_type
            '''
            , {'season': season, 'season_type': season_type, 'team_id': team_id}
        )
        standings = run_query(
            '''
            SELECT wins, losses, win_pct
            FROM staging_marts.dim_standings
            WHERE team_id = :team_id
                AND season = :season
                AND league_id = '00'
            '''
            , {'team_id': team_id, 'season': season, 'season_type': season_type}
        )
        return (core.iloc[0] if not core.empty else None, standings.iloc[0] if not standings.empty else None)

    core_L, standings_L = get_team_data(team_id_L, season_L, type_L)
    core_R, standings_R = get_team_data(team_id_R, season_R, type_R)

    st.markdown(
    f"""
    <div style="display:flex; align-items:center; justify-content:center; gap:60px; margin-bottom:1.5rem;">
        <div style="text-align:center;">
            <img src="https://cdn.nba.com/logos/nba/{team_id_L}/global/L/logo.svg" width="300">
            <div style="font-size:24px; font-weight:700; margin-top:8px;">{team_name_L}</div>
            <div style="font-size:13px; color:#9A9EA6;">{season_L} · {type_L}</div>
            {"<div style='font-weight:600; margin-top:4px;'>" + f"{int(standings_L['wins'])}-{int(standings_L['losses'])} ({standings_L['win_pct']:.1%})" + "</div>" if standings_L is not None else ""}
        </div>
        <div style="text-align:center;">
            <img src="https://cdn.nba.com/logos/nba/{team_id_R}/global/L/logo.svg" width="300">
            <div style="font-size:24px; font-weight:700; margin-top:8px;">{team_name_R}</div>
            <div style="font-size:13px; color:#9A9EA6;">{season_R} · {type_R}</div>
            {"<div style='font-weight:600; margin-top:4px;'>" + f"{int(standings_R['wins'])}-{int(standings_R['losses'])} ({standings_R['win_pct']:.1%})" + "</div>" if standings_R is not None else ""}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

    st.divider()

    def row(label, key, fmt, higher_is_better=True):
        if core_L is None or core_R is None:
            return 
        l, r = core_L[key], core_R[key]
        l_display = fmt.format(l) if l is not None else "-"
        r_display = fmt.format(r) if r is not None else "-"
        st.markdown(comparison_row_html(label, l, r, l_display, r_display, higher_is_better), unsafe_allow_html=True)

    st.markdown("<p style='color:#9A9EA6; font-size:20px; margin-bottom:4px;margin-left:865px'>Core</p>", unsafe_allow_html=True)
    row("Offensive Rating", 'offensive_rating', "{:.1f}")
    row("Defensive Rating", 'defensive_rating', "{:.1f}", higher_is_better=False)
    row("Net Rating", 'net_rating', "{:.1f}")
    row("Pace", 'pace', "{:.1f}")

    st.write("")
    st.markdown("<p style='color:#9A9EA6; font-size:20px; margin-bottom:4px;margin-left:810px'>Four Factors - Offense</p>", unsafe_allow_html=True)
    row("eFG%", 'efg_pct', "{:.1%}")
    row("TOV%", 'tov_pct', "{:.1f}%", higher_is_better=False)
    row("OREB%", 'oreb_pct', "{:.1%}")
    row("FTR%", 'ftr', "{:.1%}")

    st.write("")
    st.markdown("<p style='color:#9A9EA6; font-size:20px; margin-bottom:4px;margin-left:800px'>Four Factors - Defense</p>", unsafe_allow_html=True)
    row("Opp eFG%", 'efg_pct', "{:.1%}", higher_is_better=False)
    row("Opp TOV%", 'opp_tov_pct', "{:.1f}%")
    row("DREB%", 'dreb_pct', "{:.1%}")
    row("Opp FTR%", 'opp_ftr', "{:.1%}")

else:
    grain = st.radio("Grain", ["Per Game", "Per 36", "Per 75", "Per 100"], horizontal=True)

    GRAIN_STATS_TABLE = {
        "Per Game": "fct_player_season_summary",
        "Per 36": "fct_player_stats_per_36",
        "Per 75": "fct_player_stats_per_75",
        "Per 100": "fct_player_stats_per_100",
    }

    GRAIN_COLS = {
        "pts": ("pts_per_game", "pts"), "reb": ("rebs_per_game", "reb"), "ast": ("asts_per_game", "ast"),
        "stl": ("stls_per_game", "stl"), "blk": ("blks_per_game", "blk"), "tov": ("tovs_per_game", "tov")
    }

    def grain_col(stat, grain):
        game_stat, suf = GRAIN_COLS[stat]
        if grain == "Per Game":
            return game_stat
        tag = {"Per 36": "36", "Per 75": "75", "Per 100": "100"}[grain]
        return f"{suf}_per_{tag}"

    col_left, col_right = st.columns(2)
    def player_filters(col, side_key):
        with col:
            season = st.selectbox("Season", available_seasons(), key=f"season_{side_key}")
            season_type = st.selectbox("Season Type", ["Regular Season", "Playoffs"], key=f"type_{side_key}")
            teams = run_query(
                '''
                SELECT DISTINCT team_id
                    , team_name
                FROM staging_marts.dim_standings
                WHERE season = :season
                    AND league_id = '00'
                ORDER BY 2
                '''
                , {'season': season}
            )
            team_filter = st.selectbox("Team", ["All Teams"] + teams['team_name'].tolist(), key=f"pteam_{side_key}")
            team_clause = "" if team_filter == "All Teams" else "AND lt.team_id = :team_id"
            p_params = {"season": season, "season_type": season_type}
            if team_filter != "All Teams":
                p_params['team_id'] = teams.loc[teams['team_name'] == team_filter, 'team_id'].iloc[0]

            players = run_query(
                f'''
                WITH player_latest_team AS (
                    SELECT player_id
                        , team_id
                        , ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY game_date) AS rn
                    FROM staging_marts.fct_player_games
                    WHERE season = :season
                        AND league_id = '00'
                        AND season_type = :season_type
                )
                SELECT DISTINCT s.player_id
                    , s.player_name
                    , lt.team_id
                FROM staging_marts.fct_player_season_summary s
                JOIN player_latest_team lt ON lt.player_id = s.player_id
                    AND lt.rn = 1
                WHERE s.season = :season
                    AND s.league_id = '00'
                    AND s.season_type = :season_type
                    {team_clause}
                ORDER BY 2
                '''
                , p_params
            )
            player_name = st.selectbox("Player", players['player_name'], key=f"player_{side_key}")
            row = players.loc[players['player_name'] == player_name].iloc[0]
        return season, season_type, row['player_id'], row['team_id'], player_name

    season_L, type_L, player_id_L, team_id_L, player_name_L = player_filters(col_left, "PL")
    season_R, type_R, player_id_R, team_id_R, player_name_R = player_filters(col_right, "PR")

    def get_player_data(player_id, team_id, season, season_type):
        stats_table = GRAIN_STATS_TABLE[grain]
        cols = [grain_col(s, grain) for s in GRAIN_COLS]
        p = {"player_id": player_id, "team_id": team_id, "season": season, "season_type": season_type}

        grain_stats = run_query(
            f'''
            SELECT {", ".join(cols)}
            FROM staging_marts.{stats_table}
            WHERE player_id = :player_id
                AND team_id = :team_id
                AND season = :season
                AND season_type = :season_type
            '''
            , p
        )
        grain_stats = grain_stats.iloc[0] if not grain_stats.empty else None

        constants = run_query(
            '''
            SELECT games_played, minutes_per_game, fg2_pct, fg3_pct, ft_pct, fg3pr, ftr
                , ts_pct, relative_ts_pct, oreb_pct, dreb_pct, reb_pct, stl_pct, blk_pct, net_rating, tov_pct, assist_pct
            FROM staging_marts.fct_player_season_summary
            WHERE player_id = :player_id
                AND team_id = :team_id
                AND season = :season
                AND season_type = :season_type
            '''
            , p
        )
        constants = constants.iloc[0] if not constants.empty else None

        bio = run_query(
        '''
        SELECT dp.player_name
            , dp.position
            , dp.height
            , dp.weight
            , dt.full_name AS team_name
        FROM staging_marts.dim_players dp
        LEFT JOIN staging_marts.dim_teams dt ON dt.team_id = :team_id
        WHERE dp.player_id = :player_id
        '''
            , {'player_id': player_id, 'team_id': team_id}
        )
        bio = bio.iloc[0] if not bio.empty else None
        return grain_stats, constants, bio

    grain_stats_L, constants_L, bio_L = get_player_data(player_id_L, team_id_L, season_L, type_L)
    grain_stats_R, constants_R, bio_R = get_player_data(player_id_R, team_id_R, season_R, type_R)

    def player_id_block(player_id, bio, season, season_type):
        if bio is None:
            return f"<div style='text-align:center;'>No data available</div>"
        return f"""
        <div style="text-align:center;">
            <img src="https://cdn.nba.com/headshots/nba/latest/260x190/{player_id}.png" width="200">
            <div style="font-size:24px; font-weight:700; margin-top:8px;">{bio['player_name']}</div>
            <div style="font-size:14px; color:#9A9EA6;">{bio['position']} | {bio['team_name']}</div>
            <div style="font-size:13px; color:#9A9EA6;">{season} | {season_type}</div>
        </div>
        """

    st.markdown(
        f"""
        <div style="display:flex; align-items:center; justify-content:center; gap:60px; margin-bottom:1.5rem;">
            {player_id_block(player_id_L, bio_L, season_L, type_L)}
            {player_id_block(player_id_R, bio_R, season_R, type_R)}
        </div>
        """, unsafe_allow_html=True
    )

    st.divider()

    def grain_row(label, stat, higher_is_better=True):
        if grain_stats_L is None or grain_stats_R is None:
            return
        key = grain_col(stat, grain)
        l, r = grain_stats_L[key], grain_stats_R[key]
        st.markdown(comparison_row_html(label, l, r, f"{l:.1f}", f"{r:.1f}", higher_is_better), unsafe_allow_html=True)

    FMT = {"pct": "{:.1%}", "signed_pct": "{:+.1%}", "signed": "{:+.1f}", "tov": "{:.1f}%", "int": "{:.0f}"}

    def const_row(label, key, fmt="pct", higher_is_better=True):
        if constants_L is None or constants_R is None:
            return 
        l, r = constants_L[key], constants_R[key]
        
        f = FMT[fmt]
        st.markdown(comparison_row_html(label, l, r, f.format(l), f.format(r), higher_is_better), unsafe_allow_html=True)

    st.markdown("<p style='color:#9A9EA6; font-size:24px; margin-bottom:4px; margin-left:830px;'>Production</p>", unsafe_allow_html=True)
    const_row("Games Played", "games_played", "int")
    const_row("Minutes Per Game", "minutes_per_game", "int")
    grain_row("PTS", "pts")
    grain_row("REB", "reb")
    grain_row("AST", "ast")
    grain_row("STL", "stl")
    grain_row("BLK", "blk")
    grain_row("TOV", "tov", higher_is_better=False)

    st.write("")
    st.markdown("<p style='color:#9A9EA6; font-size:24px; margin-bottom:4px; margin-left: 830px;'>Shooting</p>", unsafe_allow_html=True)
    const_row("2PT%", "fg2_pct")
    const_row("3PT%", "fg3_pct")
    const_row("FT%", "ft_pct")
    const_row("3PA Rate", "fg3pr")
    const_row("FTR", "ftr")
    const_row("TS%", "ts_pct")
    const_row("rTS", "relative_ts_pct", "signed_pct")

    st.write("")
    st.markdown("<p style='color:#9A9EA6; font-size:24px; margin-bottom:4px; margin-left:830px;'>Advanced</p>", unsafe_allow_html=True)
    const_row("OREB%", "oreb_pct")
    const_row("DREB%", "dreb_pct")
    const_row("REB%", "reb_pct")
    const_row("AST%", "assist_pct")

    const_row("STL%", "stl_pct")
    const_row("BLK%", "blk_pct")
    const_row("TOV%", "tov_pct", "tov", higher_is_better=False)
    const_row("Net RTG", "net_rating", "signed")