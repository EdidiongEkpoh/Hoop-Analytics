import streamlit as st
from db import run_query, available_seasons
from ui import inject_css, percentile_badge_html, draw_court
import plotly.graph_objects as go
import pandas as pd
inject_css()

st.markdown(
    '''
    <div style="display:flex; justify-content:center; align-items:center;  margin-bottom:1rem;">
        <h1 style="margin:0;">Player Profile</h1>
    </div>
    ''', unsafe_allow_html=True
)

col_a, col_b, col_c = st.columns(3)
season = col_a.selectbox("Season", available_seasons())
league_id = col_b.selectbox("League", ["00"], format_func=lambda x: {"00": "NBA"}[x])
season_type = col_c.selectbox('Season Type', ['Regular Season', 'Playoffs'])

teams = run_query(
    '''
    SELECT DISTINCT team_id
        , team_name
    FROM staging_marts.dim_standings
    WHERE season = :season
        AND league_id = :league_id
    ORDER BY 2
    ''',
    {"season": season, "league_id": league_id}
)
team_filter = st.selectbox("Team", ["All Teams"] + teams["team_name"].tolist())
team_clause = "" if team_filter == "All Teams" else "AND lt.team_id = :team_id"
player_params = {"season": season, "league_id": league_id, "season_type": season_type}
if team_filter != "All Teams":
    player_params["team_id"] = teams.loc[teams['team_name'] == team_filter, "team_id"].iloc[0]

players = run_query(
    f'''
    WITH player_latest_team AS (
        SELECT player_id
            , team_id
            , ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY game_date DESC) AS rn
        FROM staging_marts.fct_player_games
        WHERE season = :season
            AND league_id = :league_id
            AND season_type = :season_type
    )
    SELECT DISTINCT s.player_id
        , s.player_name
        , lt.team_id
    FROM staging_marts.fct_player_season_summary s 
    JOIN player_latest_team lt ON lt.player_id = s.player_id
        AND rn = 1
    WHERE s.season = :season
        AND s.league_id = :league_id
        AND s.season_type = :season_type
        {team_clause}
    ORDER BY 2
    ''', player_params
)

player_name = st.selectbox("Player", players["player_name"])
row = players.loc[players["player_name"] == player_name].iloc[0]
player_id, team_id = row['player_id'], row['team_id']

params = {'player_id': player_id, "team_id": team_id, "season": season, "league_id": league_id, "season_type": season_type}


bio = run_query(
    '''
    WITH current_info AS (
        SELECT player_id
            , team_id
            , season
            , league_id
            , jersey_number
            , age
        FROM staging_staging.stg_team_rosters
        WHERE player_id = :player_id
            AND team_id = :team_id
            AND season = :season
            AND league_id = :league_id
    )
    SELECT dp.player_name, dp.position, dp.height, dp.weight, dp.birthdate
        , dp.school, dp.country
        , dp.draft_year
        , CASE 
            WHEN dp.draft_round = '1' THEN dp.draft_number
            WHEN dp.draft_round = '2' THEN CAST((CAST(dp.draft_number AS INTEGER)+30) AS VARCHAR)
          ELSE 'Undrafted' END AS draft_pick
        , dt.full_name AS team_name, dt.abbreviation
        , ci.jersey_number
        , ci.age
    FROM staging_marts.dim_players dp
    LEFT JOIN staging_marts.dim_teams dt ON dt.team_id = :team_id
    LEFT JOIN current_info ci ON ci.player_id = dp.player_id
    WHERE dp.player_id = :player_id
    '''
    , params
).iloc[0]

draft_line = f"Undrafted in {bio['draft_year']}" if bio['draft_pick'] == 'Undrafted' else f"Pick #{bio['draft_pick']} in {bio['draft_year']}"
season_stats = run_query(
    '''
    SELECT pts_per_game
        , rebs_per_game
        , asts_per_game
        , stls_per_game
        , blks_per_game
        , fg2_pct
        , fg3_pct
        , ft_pct
        , fg3pr
        , ftr
        , ts_pct
        , games_played
    FROM staging_marts.fct_player_season_summary
    WHERE player_id = :player_id
        AND team_id = :team_id
        AND season = :season
        AND season_type = :season_type
    ''',
    params
).iloc[0]





def grain_col(stat, grain, kind):
    game_stat, suf, game_pctl, pctl_suf = GRAIN_COLS[stat]
    if grain == "Per Game":
        return game_stat if kind == "stat" else game_pctl
    tag = {"Per 36": "36", "Per 75": "75", "Per 100": "100"}[grain]
    return f"{suf}_per_{tag}" if kind == "stat" else f"{pctl_suf}_per_{tag}_percentile"

def safe_badge(pctl_row, col_name, higher_is_better):
    if pctl_row[col_name] is None:
        return "<span style='color:#6B7280; font-size:12px;'></span>"
    return percentile_badge_html(pctl_row[col_name], higher_is_better)
GRAIN_STATS_TABLE = {
    "Per Game": "fct_player_season_summary",
    "Per 36": "fct_player_stats_per_36",
    "Per 75": "fct_player_stats_per_75",
    "Per 100": "fct_player_stats_per_100"
}

GRAIN_PCTL_TABLE = {
    "Per Game": "fct_player_percentiles_per_game",
    "Per 36": "fct_player_percentiles_per_36",
    "Per 75": "fct_player_percentiles_per_75",
    "Per 100": "fct_player_percentiles_per_100"
}

GRAIN_COLS = {
    "pts": ("pts_per_game", "pts", "ppg_percentile", "pts"),
    "reb": ("rebs_per_game", "reb", "reb_percentile", "reb"),
    "ast": ("asts_per_game", "ast", "ast_percentile", "ast"),
    "stl": ("stls_per_game", "stl", "stl_percentile", "stl"),
    "blk": ("blks_per_game", "blk", "blk_percentile", "blk"),
    "tov": ("tovs_per_game", "tov", "tov_percentile", "tov"),
}
rad1, rad2 = st.columns([0.67, 1])
with rad2:
    grain = st.radio("Grain", ["Per Game", "Per 36", "Per 75", "Per 100"], horizontal=True, label_visibility="collapsed")
stats_table, pctl_table = GRAIN_STATS_TABLE[grain], GRAIN_PCTL_TABLE[grain]

counting_cols = [grain_col(s, grain, "stat") for s in GRAIN_COLS]
counting_pctl_cols = [grain_col(s, grain, "pctl") for s in GRAIN_COLS]

grain_stats = run_query(
    f'''
    SELECT {", ".join(counting_cols)}
    FROM staging_marts.{stats_table}
    WHERE player_id = :player_id
        AND team_id = :team_id
        AND league_id = :league_id
        AND season_type = :season_type
        AND season = :season
    ''',
    params
)
grain_stats = grain_stats.iloc[0] if not grain_stats.empty else None

grain_pctl = run_query(
    f'''
    SELECT {", ".join(counting_pctl_cols)}
    FROM staging_marts.{pctl_table}
    WHERE player_id = :player_id
        AND team_id = :team_id
        AND league_id = :league_id
        AND season_type = :season_type
        AND season = :season
    ''',
    params
)

grain_pctl = grain_pctl.iloc[0] if not grain_pctl.empty else None
constants = run_query(
    '''
    SELECT fg_pct, fg2_pct, fg3_pct, ft_pct, ftr, fg3pr, efg_pct, ts_pct, relative_ts_pct
        , usage, oreb_pct, dreb_pct, reb_pct, assist_pct, stl_pct, blk_pct, tov_pct
        , offensive_rating, defensive_rating, net_rating, games_played, minutes_per_game
    FROM staging_marts.fct_player_season_summary
    WHERE player_id = :player_id
        AND team_id = :team_id
        AND season = :season
        AND season_type = :season_type
    ''',
    params
)
constants = constants.iloc[0] if not constants.empty else None
constants_pctl = run_query(
    '''
    SELECT fg_pct_percentile, fg2_pct_percentile, fg3_pct_percentile, ft_pct_percentile
        , ftr_percentile, fg3pr_percentile, efg_percentile, ts_percentile
        , usage_percentile, stl_pct_percentile, blk_pct_percentile
        , off_rating_percentile, def_rating_percentile, net_rating_percentile, ast_pct_percentile
        , tov_pct_percentile, oreb_pct_percentile, dreb_pct_percentile, reb_pct_percentile
    FROM staging_marts.fct_player_percentiles_per_game
    WHERE player_id = :player_id
        AND team_id = :team_id
        AND season = :season
        AND season_type = :season_type
    ''',
    params
)

constants_pctl = constants_pctl.iloc[0] if not constants_pctl.empty else None

def grain_metric(col, stat, label, higher_is_better=True):
    if grain_stats is None:
        col.metric(label, '-')
        return
    col.metric(label, f"{grain_stats[grain_col(stat, grain, 'stat')]:.1f}")
    col.markdown(safe_badge(grain_pctl, grain_col(stat, grain, 'pctl'), higher_is_better), unsafe_allow_html=True)

def const_metric(col, key, label, pctl_key=None, higher_is_better=True, fmt="pct"):
    if constants is None:
        col.metric(label, '-')
        return 
    value = constants[key]
    display = {"pct": f"{value:.1%}", "signed_pct": f"{value:+.1%}", "signed": f"{value:+.1f}", 'tov': f"{value:.1f}%"}[fmt]
    col.metric(label, display)
    if pctl_key:
        col.markdown(safe_badge(constants_pctl, pctl_key, higher_is_better), unsafe_allow_html=True)

photo_col, info_col, stats_col = st.columns([1, 2, 4.5], vertical_alignment="top")
photo_col.image(f"https://cdn.nba.com/headshots/nba/latest/260x190/{player_id}.png", width=200)


with info_col:
    st.markdown(f"<div style='font-size:45px; font-weight:700; margin-bottom:2px;'>{bio['player_name']}</div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="font-size:16px; font-weight:600; margin-bottom:2px;">
            <span style='margin-right: 8px;'>{bio['position']} #{bio['jersey_number']} | {bio['team_name']} | {bio['height']}, {int(bio['weight'])} lbs | {bio['age']} years old</span>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div style="font-size:14px; color:#9A9EA6; margin-bottom:100px;">
            <span style="margin-right: 8px;">{draft_line} Draft | School/Club: {bio['school']}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    

with stats_col:
    h1, h2, h3, h4, h5 = st.columns(5)
    h1.metric("GP", f"{constants['games_played']:.0f}" if constants is not None else '-')
    h2.metric("MIN", f"{constants['minutes_per_game']:.0f}" if constants is not None else '-')
    grain_metric(h3, "pts", "PTS")
    grain_metric(h4, "reb", "REB")
    grain_metric(h5, "ast", "AST")

    h6, h7, h8 = st.columns(3)
    grain_metric(h6, "stl", "STL")
    grain_metric(h7, "blk", "BLK")
    grain_metric(h8, "tov", "TOV")

st.write("")


row1, row2 = st.columns([2, 4.5])

with row1:
    r1 = st.columns(3)
    const_metric(r1[0], 'fg2_pct', '2PT%', 'fg2_pct_percentile')
    const_metric(r1[1], 'fg3_pct', '3PT%', 'fg3_pct_percentile')
    const_metric(r1[2], 'ft_pct', 'FT%', 'ft_pct_percentile')

with row2:
    r2 = st.columns(4)
    const_metric(r2[0], 'fg3pr', '3PA Rate', 'fg3pr_percentile')
    const_metric(r2[1], 'ftr', 'FTR', 'ftr_percentile')
    const_metric(r2[2], 'ts_pct', 'TS%', 'ftr_percentile')
    const_metric(r2[3], "relative_ts_pct", "rTS%", pctl_key=None, fmt="signed_pct")


row3, row4 = st.columns([2, 4.5])
with row3:
    r3 = st.columns(3)
    const_metric(r3[0], 'oreb_pct', 'OREB%', 'oreb_pct_percentile')
    const_metric(r3[1], "dreb_pct", "DREB%", "dreb_pct_percentile")
    const_metric(r3[2], "reb_pct", "REB%", "reb_pct_percentile")

with row4:
    r4 = st.columns(3)
    const_metric(r4[0], "assist_pct", "AST%", "ast_pct_percentile")
    const_metric(r4[1], "tov_pct", "TOV%", "tov_pct_percentile", higher_is_better=False, fmt="tov")
    r4[2].metric("Net RTG", f"{constants['net_rating']:.1f}")
   



st.divider()


tab_performance, tab_shooting, tab_tracking, tab_games = st.tabs(['Performance Trend', 'Shooting', 'Shot Profile', 'Game Log'])

with tab_performance:
    st.markdown(
    '''
    <div style="display:flex; justify-content:center; align-items:center;margin-bottom:1rem;margin-left: 175px;">
        <h1 style="margin:0; font-size: 35px;">Performance Trend</h1>
    </div>
    ''', unsafe_allow_html=True
    )

    trend_col1, trend_col2 = st.columns([1, 3])
    stat_choice = trend_col1.selectbox("Stat", ["PTS", "REB", "AST", "STL", "BLK", "TS", "Net Rating"])
    window = trend_col1.select_slider("Rolling Window (games)", options=[5, 10, 15], value=10)

    trend = run_query(
        '''
        SELECT game_date, pts, reb, ast, stl, blk, fgm, fga, fta, net_rating, wl
        FROM staging_marts.fct_player_games
        WHERE player_id = :player_id
            AND season = :season
            AND league_id = :league_id
            AND season_type = :season_type
        ORDER BY 1
        ''',
        params
    )

    denom = 2 * (trend['fga'] + 0.44 * trend['fta'])
    trend['ts_pct'] = trend['pts'] / denom.replace(0, pd.NA)
    STAT_OPTIONS = {
        "PTS": dict(col="pts", label="Points", hover=":.0f", axis_fmt=None),
        "REB": dict(col="reb", label="Rebounds", hover=":.0f", axis_fmt=None),
        "AST": dict(col="ast", label="Assists", hover=":.0f", axis_fmt=None),
        "STL": dict(col="stl", label="Steals", hover=":.0f", axis_fmt=None),
        "BLK": dict(col="blk", label="Blocks", hover=":.0f", axis_fmt=None),
        "TS": dict(col="ts_pct", label="True Shooting %", hover=":.1%", axis_fmt=".0%"),
        "Net Rating": dict(col="net_rating", label="Net Rating", hover=":+.1f", axis_fmt=None),
    }
    stat_cfg = STAT_OPTIONS[stat_choice]
    stat_col = stat_cfg['col']

    trend['rolling_value'] = trend[stat_col].rolling(window=window, min_periods=1).mean()
    ref_value = 0 if stat_choice == "Net Rating" else trend[stat_col].mean()

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=trend['game_date'], y=trend[stat_col], mode='markers', name=f"Game {stat_choice}",
        marker=dict(size=6, opacity=1, color=trend['wl'].map({'W':'#5DCAA5', 'L': '#E05C5C'})),
        hovertemplate=f'%{{x|%b %d}}: %{{y{stat_cfg['hover']}}}<extra></extra>'
    ))
    fig3.add_hline(
        y=ref_value, line_dash="dash", line_color="#9A9EA6", opacity=0.6,
        annotation_text="League AVG" if stat_choice != 'Net Rating' else '',
        annotation_font_color="#9A9EA6"
    )
    fig3.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="#E8E8E8", family="Inter", size=13),
        xaxis=dict(gridcolor="#2A2E37", title=None),
        yaxis=dict(gridcolor="#2A2E37", title=stat_cfg['label'], tickformat=stat_cfg['axis_fmt']),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=350, margin=dict(l=40, r=20, t=40, b=20)
    )
    trend_col2.plotly_chart(fig3, use_container_width=True)

with tab_shooting:
    st.markdown(
    '''
    <div style="display:flex; justify-content:center; align-items:center;margin-bottom:1rem;margin-left: 175px;">
        <h1 style="margin:0; font-size: 35px;">Shot Chart</h1>
    </div>
    ''', unsafe_allow_html=True
    )

    shots = run_query(
        '''
        SELECT loc_x  
            , loc_y
            , shot_made_flag
            , shot_type
            , shot_zone_basic
        FROM staging_staging.stg_shot_chart_detail
        WHERE player_id = :player_id
            AND team_id = :team_id
            AND season = :season
            AND league_id = :league_id
            AND season_type = :season_type
        ''',
        params
    )

    def shot_summary(df):
        fga = len(df)
        fgm = int(df['shot_made_flag'].sum()) if fga > 0 else 0
        pct = fgm / fga if fga > 0 else 0
        return fgm, fga, pct

    def fmt_shot_line(made, att, pct):
        return "0 / 0" if att == 0 else f"{made} / {att} ({pct:.1%})"

    overall = shot_summary(shots)
    threes = shot_summary(shots[shots['shot_type'] == "3PT Field Goal"])
    twos = shot_summary(shots[shots['shot_type'] == "2PT Field Goal"])
    rim = shot_summary(shots[shots['shot_zone_basic'] == "Restricted Area"])
    non_rim_paint = shot_summary(shots[shots['shot_zone_basic'] == "In The Paint (Non-RA)"])
    middies = shot_summary(shots[shots['shot_zone_basic'] == "Mid-Range"])

    s1, s2, s3, s4, s5, s6 = st.columns(6)
    s1.metric("FG", fmt_shot_line(*overall))
    s2.metric("2PT", fmt_shot_line(*twos))
    s3.metric("3PT", fmt_shot_line(*threes))
    s4.metric("Mid-Range", fmt_shot_line(*middies)) 
    s5.metric("Rim", fmt_shot_line(*rim))
    s6.metric("Non-Rim Paint", fmt_shot_line(*non_rim_paint))
    

    st.write("")  
    fig_court = go.Figure()
    draw_court(fig_court)

    misses = shots[shots['shot_made_flag'] == 0]
    makes = shots[shots['shot_made_flag'] == 1]

    fig_court.add_trace(go.Scatter(
        x=misses['loc_x'], y=misses['loc_y'], mode="markers", name="Miss",
        marker=dict(color='#E05C5C', size=5, symbol='x', opacity=1), hoverinfo='skip'
    ))
    fig_court.add_trace(go.Scatter(
            x=makes['loc_x'], y=makes['loc_y'], mode="markers", name="Make",
            marker=dict(color='#5DCAA5', size=5, symbol='9', opacity=1), hoverinfo='skip'
    ))

    fig_court.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="#E8E8E8", family="Inter", size=13),

        xaxis=dict(range=[260, -260], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[-60, 60], showgrid=False, zeroline=False, showticklabels=False, scaleanchor='x', scaleratio=1),
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
        height=550, margin=dict(l=10, r=10, t=40, b=10)
    )

    st.plotly_chart(fig_court, use_container_width=True)

    st.write("")

    st.markdown(
        '''
        <div style="display:flex; justify-content:center; align-items:center;margin-bottom:1rem;margin-left: 175px;">
            <h1 style="margin:0; font-size: 35px;">Shot Zones vs League Average</h1>
        </div>
        ''', unsafe_allow_html=True
        )

    shot_zones = run_query(
        '''
        WITH player_zones AS (
            SELECT shot_zone_basic
                , SUM(fga) AS fga
                , SUM(fgm) AS fgm
            FROM staging_marts.fct_shot_zone_summary
            WHERE player_id = :player_id
                AND team_id = :team_id
                AND season = :season
                AND season_type = :season_type
                AND league_id = :league_id
            GROUP BY 1
        )
        , league_zones AS (
            SELECT shot_zone_basic
                , SUM(fga) AS league_fga
                , SUM(fgm) AS league_fgm
            FROM staging_marts.fct_shot_zone_summary
            WHERE season = :season
                AND season_type = :season_type
                AND league_id = :league_id
            GROUP BY 1
        )
        SELECT pz.shot_zone_basic
            , pz.fga
            , pz.fgm::NUMERIC / NULLIF(pz.fga, 0) AS fg_pct
            , lz.league_fgm::NUMERIC / NULLIF(lz.league_fga, 0) AS league_fg_pct
            , (pz.fgm::NUMERIC / NULLIF(pz.fga, 0)) - (lz.league_fgm::NUMERIC / NULLIF(lz.league_fga, 0)) AS fg_pct_vs_league
        FROM player_zones pz
        LEFT JOIN league_zones lz ON lz.shot_zone_basic = pz.shot_zone_basic
        ORDER BY 2 DESC
        ''',
        params
        )
    fig_zones = go.Figure(go.Bar(
        x=shot_zones['fga'], y=shot_zones['shot_zone_basic'], orientation='h',
        marker=dict(
                color=shot_zones['fg_pct_vs_league'], colorscale="RdYlGn", cmid=0, showscale=True, 
                colorbar=dict(title="Vs League Average", tickformat="+.0%")
        ),
        customdata=shot_zones[['fg_pct', 'league_fg_pct']], 
        hovertemplate="%{y}: %{x} attempts<br>Player FG%: %{customdata[0]:.1%}<br>League FG%: %{customdata[1]:.1%}<extra></extra>",
    ))
    fig_zones.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="#E8E8E8", family="Inter", size=13),
        xaxis=dict(gridcolor="#2A2E37", title="Attempts"),
        yaxis=dict(title=None), height=300, margin=dict(l=10, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_zones, use_container_width=True)

GRAIN_TRACKING_TABLE = {
    "Total": "fct_player_tracking_stats",
    "Per Game": "fct_player_tracking_stats_per_game",
    "Per 36": "fct_player_tracking_stats_per_36",
    "Per 75": "fct_player_tracking_stats_per_75",
    "Per 100": "fct_player_tracking_stats_per_100"
}

with tab_tracking:
    tracking_grain = st.radio("Grain", ["Total", "Per Game", "Per 36", "Per 75", "Per 100"], horizontal=True, label_visibility="collapsed")
    tracking_table = GRAIN_TRACKING_TABLE[tracking_grain]
    suffix = "" if tracking_grain == "Total" else f"_per_{tracking_grain.split()[-1]}"

    tp = run_query(
        '''
        SELECT catch_shoot_fg_pct, catch_shoot_fg3_pct, catch_shoot_efg
            , pullup_fg_pct, pullup_fg3_pct, pullup_efg_pct
            , drive_fg_pct
            , post_touch_fg_pct
            , pct_ast_fgm, pct_uast_fgm, pct_ast_2pm, pct_uast_2pm, pct_ast_3pm, pct_uast_3pm
        FROM staging_marts.fct_player_tracking_stats
        WHERE player_id = :player_id
            AND team_id = :team_id
            AND season = :season
            AND league_id = :league_id
        '''
        , params
    )

    tp = tp.iloc[0] if not tp.empty else None

    tc = run_query(

        f'''
        SELECT catch_shoot_fgm{suffix} AS cs_fgm, catch_shoot_fga{suffix} AS cs_fga, catch_shoot_pts{suffix} AS cs_pts
            , pullup_fgm{suffix} AS pu_fgm, pullup_fga{suffix} AS pu_fga, pullup_pts{suffix} AS pu_pts
            , drive_fgm{suffix} AS d_fgm, drive_fga{suffix} AS d_fga, drive_pts{suffix} AS d_pts
            , drive_ast{suffix} AS d_ast, drive_tov{suffix} AS d_tov
            , post_touch_fgm{suffix} AS pt_fgm, post_touch_fga{suffix} AS pt_fga, post_touch_pts{suffix} AS pt_pts
            , post_touch_ast{suffix} AS pt_ast, post_touch_tov{suffix} AS pt_tov
        FROM staging_marts.{tracking_table}
        WHERE player_id = :player_id
            AND team_id = :team_id
            AND season = :season
            AND season_type = :season_type
        '''
        , params
    )
    tc = tc.iloc[0] if not tc.empty else None

    def tracking_line(made, att, pct, grain):
        if tc is None or att is None:
            return "-"
        if grain == "Total":
            return f"{made:.0f} / {att:.0f} ({pct:.1%})" if pct is not None else f"{made:.0f} / {att:.0f}"
        return f"{made:.1f} / {att:.1f} ({pct:.1%})" if pct is not None else f"{made:.1f} / {att:.1f}"
    st.markdown(
        '''
        <div style="display:flex; justify-content:center; align-items:center;margin-bottom:1rem;margin-left: 175px;">
            <h1 style="margin:0; font-size: 35px;">Shot Type Breakdown</h1>
        </div>
        ''', unsafe_allow_html=True
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.caption(":red[Catch & Shoot]")
        st.metric("FGM/FGA", tracking_line(tc['cs_fgm'], tc['cs_fga'], tp['catch_shoot_fg_pct'], tracking_grain) if tc is not None and tp is not None else "-")
        if tracking_grain == "Total":
            st.metric("PTS", f"{tc['cs_pts']:.0f}" if tc is not None else "-")
        else:
            st.metric("PTS", f"{tc['cs_pts']:.1f}" if tc is not None else "-")
    with c2:
        st.caption(":red[Pull Ups]")
        st.metric("FGM/FGA", tracking_line(tc['pu_fgm'], tc['pu_fga'], tp['pullup_fg_pct'], tracking_grain) if tc is not None and tp is not None else "-")
        if tracking_grain == "Total":
            st.metric("PTS", f"{tc['pu_pts']:.0f}" if tc is not None else "-")
        else:
            st.metric("PTS", f"{tc['pu_pts']:.1f}" if tc is not None else "-")
    with c3:
        st.caption(":red[Drives]")
        st.metric("FGM/FGA", tracking_line(tc['d_fgm'], tc['d_fga'], tp['drive_fg_pct'], tracking_grain) if tc is not None and tp is not None else "-")
        if tracking_grain == "Total":
            st.metric("PTS", f"{tc['d_pts']:.0f}" if tc is not None else "-")
            st.metric("AST / TOV", f"{tc['d_ast']:.0f} / {tc['d_tov']:.0f}" if tc is not None else "-")
        else:
            st.metric("PTS", f"{tc['d_pts']:.1f}" if tc is not None else "-")
            st.metric("AST / TOV", f"{tc['d_ast']:.1f} / {tc['d_tov']:.1f}" if tc is not None else "-")
    with c4:
        st.caption(":red[Post Ups]")
        st.metric("FGM/FGA", tracking_line(tc['pt_fgm'], tc['pt_fga'], tp['post_touch_fg_pct'], tracking_grain) if tc is not None and tp is not None else "-")
        if tracking_grain == "Total":
            st.metric("PTS", f"{tc['pt_pts']:.0f}" if tc is not None else "-")
            st.metric("AST / TOV", f"{tc['pt_ast']:.0f} / {tc['pt_tov']:.0f}" if tc is not None else "-")
        else:
            st.metric("PTS", f"{tc['pt_pts']:.1f}" if tc is not None else "-")
            st.metric("AST / TOV", f"{tc['pt_ast']:.1f} / {tc['pt_tov']:.1f}" if tc is not None else "-")

    st.write("")
    st.markdown(
            '''
            <div style="display:flex; justify-content:center; align-items:center;margin-bottom:1rem;margin-left: 175px;">
                <h1 style="margin:0; font-size: 35px;">Assisted vs Unassisted</h1>
            </div>
            ''', unsafe_allow_html=True
        )

    if tp is not None:
        fig_ast = go.Figure()
        fig_ast.add_trace(go.Bar(
            y=["Overall", "2PT", "3PT"], x=[tp['pct_ast_fgm'], tp['pct_ast_2pm'], tp['pct_ast_3pm']],
            name='Assisted', orientation='h', marker_color="#5DCAA5", hovertemplate="%{y} %{x:.1%} assisted<extra></extra>"
        ))
        fig_ast.add_trace(go.Bar(
            y=["Overall", "2PT", "3PT"], x=[tp['pct_uast_fgm'], tp['pct_uast_2pm'], tp['pct_uast_3pm']],
            name='Unassisted', orientation='h', marker_color="#FF6B35", hovertemplate="%{y} %{x:.1%} unassisted<extra></extra>"
        ))
        fig_ast.update_layout(
            barmode='stack', plot_bgcolor='#0E1117', paper_bgcolor="#0E1117",
            font=dict(color="#E8E8E8", family="Inter", size=13),
            xaxis=dict(tickformat=".0%", gridcolor="#2A2E37"),
            yaxis=dict(title=None), legend=dict(orientation='h', yanchor='bottom', y=1.02),
            height=250, margin=dict(l=10, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_ast, use_container_width=True)
    else:
        st.caption("No tracking data available for this player/season.")
with tab_games:
    games = run_query(
        '''
        SELECT game_date, matchup, wl, minutes, pts
            , reb, ast, tov, stl, blk, pf, fgm, fga, fg3m, fg3a, ftm, fta
            , net_rating
        FROM staging_marts.fct_player_games
        WHERE team_id = :team_id
            AND league_id = :league_id 
            AND season = :season
            AND season_type = :season_type
            AND player_id = :player_id
        ORDER BY 1 DESC
        LIMIT 15
        ''',
        params
    )
    st.dataframe(games, hide_index=True, use_container_width=True, column_config={
        "game_date": st.column_config.DateColumn("Date"),
        "matchup": st.column_config.TextColumn("Matchup"),
        "wl": st.column_config.TextColumn("W/L"),
        "minutes": st.column_config.NumberColumn("MIN"),
        "pts": st.column_config.NumberColumn("PTS"),
        "reb": st.column_config.NumberColumn("REB"),
        "ast": st.column_config.NumberColumn("AST"),
        "stl": st.column_config.NumberColumn("STL"),
        "blk": st.column_config.NumberColumn("BLK"),
        "tov": st.column_config.NumberColumn("TOV"),
        "fgm": st.column_config.NumberColumn("FGM"),
        "fga": st.column_config.NumberColumn("FGA"),
        "fg3m": st.column_config.NumberColumn("3PM"),
        "fg3a": st.column_config.NumberColumn("3PA"),
        "ftm": st.column_config.NumberColumn("FTM"),
        "fta": st.column_config.NumberColumn("FTA"),
        "net_rating": st.column_config.NumberColumn("Net Rating")
    })