import streamlit as st
from db import run_query, available_seasons
from ui import conference_badge
import plotly.graph_objects as go
import requests
from PIL import Image
import io
st.set_page_config(page_title="Hoop Analytics", layout="wide")

st.markdown(
    '''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stMetric"] {
        background-color: #1A1D24;
        border: 1px solid #2A2E37;
        border-radius: 12px;
        padding: 16px 20px;
    }
    [data-testid="stMetricLabel"] {
        font-size: 13px;
        color: #9A9EA6;
    }
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 600;
    }

    h1 {
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    h2, h3 {
        font-weight: 600;
        color: #E8E8E8;
    }

    hr {
        border-color: #2A2E37;
    }
    </style>
    '''
    , unsafe_allow_html=True
)

st.markdown(
    '''
    <div style="display:flex; justify-content:center; align-items:center; gap:16px; margin-bottom:1rem;">
        <img src="https://thesvg.org/icons/nba/default.svg" width="150">
        <h1 style="margin:0">League Overview</h1>
    </div>
    ''', unsafe_allow_html=True
)
def has_playoffs(season, league_id):
    check = run_query(
        '''   
        SELECT COUNT(*) AS n
        FROM staging_marts.fct_team_games
        WHERE season = :season
            AND league_id = :league_id 
            AND season_type = 'Playoffs'
        '''
        , {"season": season, "league_id": league_id}
    )
    return check.iloc[0]['n'] > 0
col_a, col_b, col_c = st.columns(3)
season = col_a.selectbox("Season", available_seasons())
league_id = col_b.selectbox("League", ["00"], format_func=lambda x: {"00": "NBA"}[x])
season_type_options = ['Regular Season']
if has_playoffs(season, league_id):
    season_type_options.append("Playoffs")

season_type = col_c.selectbox("Season Type", season_type_options)

params = {"season": season, "league_id": league_id, "season_type": season_type}

kpis = run_query(
    '''
    SELECT AVG(pace) AS avg_pace
        , AVG(offensive_rating) AS league_ortg
        , ROUND(100.0 * AVG(CAST(fg3pr AS NUMERIC)), 2) AS fg3pr
        , ROUND(100.0 * AVG(CAST(ts_pct AS NUMERIC)), 2) AS league_ts_pct
    FROM staging_marts.fct_team_season_summary
    WHERE season = :season
        AND league_id = :league_id
        AND season_type = :season_type
    ''', 
    params
)

if kpis.empty:
    st.info(f"No {season_type.lower()} data available for {season}.")
else:
    kpis = kpis.iloc[0]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Avg Pace", f"{kpis['avg_pace']:.1f}")
    k2.metric("League ORTG", f"{kpis['league_ortg']:.1f}")
    k3.metric("3PA Rate", f"{kpis['fg3pr']:.1f}%")
    k4.metric("League TS%", f"{kpis['league_ts_pct']:.1f}%")

st.divider()

team_overview, scoring_landscape, tab_standings, tab_leaders = st.tabs(['Team Overview', 'Player Scoring', 'Standings', 'League Leaders'])

with team_overview:
    team_landscape = run_query(
    '''
    SELECT team_id
        , team_name
        , offensive_rating
        , defensive_rating
        , net_rating
    FROM staging_marts.fct_team_season_summary
    WHERE season = :season
        AND league_id = :league_id
        AND season_type = :season_type
    ''',
    params
    )

    x_range = team_landscape['offensive_rating'].max() - team_landscape['offensive_rating'].min()
    y_range = team_landscape['defensive_rating'].max() - team_landscape['defensive_rating'].min()
    img_size_x = x_range * .15
    img_size_y = y_range * .15

    fig_landscape = go.Figure()

    fig_landscape.add_trace(go.Scatter(
        x=team_landscape['offensive_rating'], y=team_landscape['defensive_rating'], mode='markers'
        , marker=dict(size=1, opacity=0), text=team_landscape['team_name'],
        hovertemplate="%{text}<br>ORTG: %{x:.1f}<br>DRTG: %{y:.1f}<extra></extra>"
    ))
    
    for _, row in team_landscape.iterrows():
        fig_landscape.add_layout_image(dict(
        source=f"https://cdn.nba.com/logos/nba/{row['team_id']}/global/L/logo.svg",
        x=row['offensive_rating'], y=row['defensive_rating'],
        xref="x", yref="y", sizex=img_size_x, sizey=img_size_y,
        xanchor="center", yanchor="middle", layer="above",
    ))


    fig_landscape.add_vline(x=team_landscape['offensive_rating'].mean(), line_dash="dash", line_color="#9A9EA6", opacity=0.5)
    fig_landscape.add_hline(y=team_landscape['defensive_rating'].mean(), line_dash="dash", line_color="#9A9EA6", opacity=0.5)
    fig_landscape.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="#E8E8E8", family="Inter", size=13),
        xaxis=dict(title="Offensive Rating", gridcolor="#2A2E37"),
        yaxis=dict(title="Defensive Rating", gridcolor="#2A2E37", autorange="reversed"),
        height=550, margin=dict(l=40, r=20, b=40)
    )
    st.plotly_chart(fig_landscape, use_container_width=True)

with scoring_landscape:
    min_mpg = st.slider("Minimum Minutes Per Game", 10, 36, 30)

    player_scoring = run_query(
        '''
        SELECT dp.player_id, dp.player_name, s.pts_per_game, s.relative_ts_pct
        FROM staging_marts.fct_player_season_summary s
        JOIN staging_staging.int_player_eligibility e ON e.player_id = s.player_id
            AND e.season = s.season
            AND e.season_type = s.season_type
            AND e.league_id = s.league_id
        JOIN staging_marts.dim_players dp ON dp.player_id = s.player_id
        WHERE s.season = :season
            AND s.league_id = :league_id
            AND s.season_type = :season_type
            AND e.meets_min_games_threshold = TRUE
            AND s.minutes_per_game >= :min_mpg
        '''
        , {**params, "min_mpg": min_mpg}
    )
    x_range = player_scoring['pts_per_game'].max() - player_scoring['pts_per_game'].min()
    y_range = player_scoring['relative_ts_pct'].max() - player_scoring['relative_ts_pct'].min()
    img_size_x = x_range * .135
    img_size_y = y_range * .135

    fig_players = go.Figure()
    fig_players.add_trace(go.Scatter(
        x=player_scoring['pts_per_game'], y=player_scoring['relative_ts_pct'],
        mode='markers', marker=dict(size=1, opacity=0), text=player_scoring['player_name'],
        hovertemplate="%{text}<br>PTS: %{x:.1f}<br>rTS%%: %{y:+.1%}<extra></extra>"
    ))

    @st.cache_data(show_spinner=False)
    def get_headshot(player_id):
        url = f"https://cdn.nba.com/headshots/nba/latest/260x190/{player_id}.png"
        try:
            resp = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            return Image.open(io.BytesIO(resp.content)).convert("RGBA")
        except Exception as e:
            return None
                
    for _, row in player_scoring.iterrows():
        if get_headshot(row['player_id']) is None:
            continue
        else:
            fig_players.add_layout_image(dict(
                source=get_headshot(row['player_id']),
                x=row['pts_per_game'], y=row['relative_ts_pct'],
                xref='x', yref='y', sizex=img_size_x, sizey=img_size_y,
                xanchor="center", yanchor="middle", layer="above"
            ))

    fig_players.add_hline(y=0, line_dash="dash", line_color="#9A9EA6", opacity=0.5)
    fig_players.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="#E8E8E8", family="Inter", size=13),
        xaxis=dict(title="Points Per Game", gridcolor="#2A2E37"),
        yaxis=dict(title="Relative TS%", gridcolor="#2A2E37", tickformat="+.0%"),
        height=550, margin=dict(l=40, r=20, t=20, b=40)
    )
    st.plotly_chart(fig_players, use_container_width=True)
with tab_standings:
    st.markdown(
        '''
        <div style="display:flex; justify-content:center; align-items:center;margin-bottom:1rem;margin-left: 175px;">
            <h1 style="margin:0; font-size: 35px;">Regular Season Standings</h1>
        </div>
        ''', unsafe_allow_html=True
    )
    standings = run_query(
        '''
        SELECT team_id
            , team_city
            , team_name
            , conference
            , wins
            , losses
            , 100.0 * CAST(wins AS FLOAT) / NULLIF(wins+losses, 0) AS win_pct
        FROM staging_marts.dim_standings
        WHERE season = :season
            AND league_id = :league_id
        ORDER BY 7 DESC
        ''',
        {"season": season, "league_id": league_id},
    )

    if league_id == "00":
        standings["logo"] = standings["team_id"].apply(lambda tid: f"https://cdn.nba.com/logos/nba/{tid}/global/L/logo.svg")
    else:
        standings["logo"] = None

    col_east, col_west = st.columns(2)
    col_east.markdown(conference_badge('Eastern Conference', '#1D6FD1'), unsafe_allow_html=True)
    col_west.markdown(conference_badge('Western Conference', '#D13B1D'), unsafe_allow_html=True)
    for conf, col in [("East", col_east), ("West", col_west)]:
        conf_df = standings[standings["conference"] == conf][
                ["logo", "team_name", "wins", "losses", "win_pct"]
            ]
        col.dataframe(
            conf_df, hide_index=True, use_container_width=True, column_config={
                "logo": st.column_config.ImageColumn("Team Logo", width="small"),
                "team_name": st.column_config.TextColumn("Team"),
                "wins": st.column_config.NumberColumn("W"),
                "losses": st.column_config.NumberColumn("L"),
                "win_pct": st.column_config.NumberColumn("Win%", format="%.1f%%")
            }
        )

st.divider()

with tab_leaders:
    st.markdown(
        '''
        <div style="display:flex; justify-content:center; align-items:center;margin-bottom:1rem;margin-left: 175px;">
            <h1 style="margin:0; font-size: 35px;">League Leaders</h1>
        </div>
        ''', unsafe_allow_html=True
    )
    grain = st.radio("Grain", ["Per game", "Per 36", "Per 75"], horizontal=True, label_visibility="collapsed")

    if grain == "Per 75":
        stats_table = 'fct_player_stats_per_75'
        pts_col, reb_col, ast_col, stl_col, blk_col, tov_col = (
            "pts_per_75", "reb_per_75", "ast_per_75", "stl_per_75", "blk_per_75", 'tov_per_75'
        )
    elif grain == "Per 36":
        stats_table = 'fct_player_stats_per_36'
        pts_col, reb_col, ast_col, stl_col, blk_col, tov_col = (
                "pts_per_36", "reb_per_36", "ast_per_36", "stl_per_36", "blk_per_36", 'tov_per_36'
        )
    else:   
        stats_table = 'fct_player_season_summary'
        pts_col, reb_col, ast_col, stl_col, blk_col, tov_col = (
                "pts_per_game", "rebs_per_game", "asts_per_game", "stls_per_game", "blks_per_game", 'tovs_per_game'
            )

    leaders = run_query(
        f'''
        SELECT DISTINCT dp.player_name
            , s.team_name
            , ROUND(s.{pts_col}, 1) AS pts
            , ROUND(s.{reb_col}, 1) AS reb
            , ROUND(s.{ast_col}, 1) AS ast
            , ROUND(s.{stl_col}, 1) AS stl
            , ROUND(s.{blk_col}, 1) AS blk
            , ROUND(s.{tov_col}, 1) AS tov
            , ROUND(100 * cast(s.fg3pr as NUMERIC), 1) as fg3pr
            , ROUND(100 * cast(s.ftr as NUMERIC), 1) as ftr
            , ROUND(100 * cast(s.ts_pct as NUMERIC), 1) as ts_pct
            , ROUND(100 * cast(s.relative_ts_pct as NUMERIC), 1) as relative_ts_pct
        FROM staging_marts.{stats_table} s
        JOIN staging_staging.int_player_eligibility e ON e.player_id = s.player_id
            AND e.season = s.season
            AND e.season_type = s.season_type
            AND e.league_id = s.league_id
        JOIN staging_marts.dim_players dp ON dp.player_id = s.player_id
        WHERE s.season = :season
            AND s.league_id = :league_id
            AND s.season_type = :season_type
            AND e.meets_min_games_threshold = TRUE
        ORDER BY 3 DESC
        ''',
        params
    )

    st.caption(f"League leaders ({grain.lower()})")
    st.dataframe(
        leaders, hide_index=True, use_container_width=True, column_config={
            "player_name": st.column_config.TextColumn("Player"),
            "team_name": st.column_config.TextColumn("Team"),
            "pts": st.column_config.NumberColumn("PTS", format="%.1f"),
            "reb": st.column_config.NumberColumn("REB", format="%.1f"),
            "ast": st.column_config.NumberColumn("AST", format="%.1f"),
            "stl": st.column_config.NumberColumn("STL", format="%.1f"),
            "blk": st.column_config.NumberColumn("BLK", format="%.1f"),
            "tov": st.column_config.NumberColumn("TOV", format="%.1f"),
            "fg3pr": st.column_config.NumberColumn("3PA Rate", format="%.1f%%"),
            "ftr": st.column_config.NumberColumn("FT Rate", format="%.1f%%"),
            "ts_pct": st.column_config.NumberColumn("TS%", format="%.1f%%"),
            "relative_ts_pct": st.column_config.NumberColumn("rTS%", format="%.1f%%"),
        }
    )