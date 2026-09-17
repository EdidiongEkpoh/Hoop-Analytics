import streamlit as st
from db import run_query, available_seasons
from ui import inject_css, rank_badge_html
import plotly.graph_objects as go

inject_css()

st.markdown(
    '''
    <div style="display:flex; justify-content:center; align-items:center;  margin-bottom:1rem;">
        <h1 style="margin:0;">Team Profile</h1>
    </div>
    ''', unsafe_allow_html=True
)

col_a, col_b, col_c, col_d = st.columns(4)
season = col_a.selectbox("Season", available_seasons())
league_id = col_b.selectbox("League", ["00"], format_func=lambda x: {"00": "NBA"}[x])
season_type = col_c.selectbox('Season Type', ['Regular Season', 'Playoffs'])

if season_type == "Playoffs":
    st.caption("Record and conference/division standings only reflect the regular season.")
    teams = run_query(
        '''
        SELECT DISTINCT ds.team_id
            , ds.team_name
        FROM staging_marts.dim_standings ds
        JOIN staging_marts.fct_team_games tg ON tg.team_id = ds.team_id
            AND tg.season = ds.season
            AND tg.league_id = ds.league_id
            AND tg.season_type = 'Playoffs'
        WHERE ds.season = :season
            AND ds.league_id = :league_id
        ORDER BY 2
        ''',
        {"season": season, "league_id": league_id}
    )
else:
    teams = run_query(
        '''
        SELECT DISTINCT ds.team_id
            , ds.team_name
        FROM staging_marts.dim_standings ds
        WHERE season = :season
            AND league_id = :league_id
        ORDER BY 2
        ''',
        {"season": season, "league_id": league_id}
    )

team_name = col_d.selectbox("Team", teams['team_name'])
team_id = teams.loc[teams["team_name"] == team_name, "team_id"].iloc[0]

params = {"team_id": team_id, "season": season, "league_id": league_id, "season_type": season_type}


header = run_query(
    '''
    WITH league_standings AS (
        SELECT team_id, team_city, team_name, conference, division, wins, losses, win_pct, current_streak, last_10_record
            , RANK() OVER (ORDER BY win_pct DESC) AS league_rank
            , RANK() OVER (PARTITION BY conference ORDER BY win_pct DESC) AS conf_rank
        FROM staging_marts.dim_standings
        WHERE season = :season
            AND league_id = :league_id
    )
    SELECT ls.*, dt.abbreviation
    FROM league_standings ls
    LEFT JOIN staging_marts.dim_teams dt ON dt.team_id = ls.team_id
    WHERE ls.team_id = :team_id
    '''
    , {"team_id": team_id, "season": season, "league_id": league_id}
).iloc[0]

ranked = run_query(
    f'''
    WITH league_stats AS (
        SELECT team_id, offensive_rating, defensive_rating, net_rating, pace
            , efg_pct, tov_pct, oreb_pct, dreb_pct, reb_pct, ftr
        FROM staging_marts.fct_team_stats_per_100
        WHERE season = :season
            AND league_id = :league_id
            AND season_type = :season_type
    )
    , opp_stats AS (
        SELECT team_id
            , opp_efg_pct
            , opp_ftr
            , opp_tov_pct
        FROM staging_marts.fct_team_opponent_stats_per_100
        WHERE season = :season
            AND league_id = :league_id
            AND season_type = :season_type
    )
    , ranked AS (
        SELECT ls.*, os.opp_efg_pct, os.opp_ftr, os.opp_tov_pct
            , COUNT(*) OVER () AS league_size
            , RANK() OVER (ORDER BY ls.offensive_rating DESC) AS ortg_rank
            , RANK() OVER (ORDER BY ls.defensive_rating) AS drtg_rank
            , RANK() OVER (ORDER BY ls.net_rating DESC) AS netrtg_rank
            , RANK() OVER (ORDER BY ls.pace DESC) AS pace_rank
            , RANK() OVER (ORDER BY ls.efg_pct DESC) AS efg_rank
            , RANK() OVER (ORDER BY ls.ftr DESC) AS ftr_rank
            , RANK() OVER (ORDER BY ls.tov_pct) AS tov_rank
            , RANK() OVER (ORDER BY ls.oreb_pct DESC) AS oreb_rank
            , RANK() OVER (ORDER BY ls.dreb_pct DESC) AS dreb_rank
            , RANK() OVER (ORDER BY os.opp_efg_pct) AS defg_rank
            , RANK() OVER (ORDER BY os.opp_ftr) AS dftr_rank
            , RANK() OVER (ORDER BY os.opp_tov_pct DESC) AS dtov_rank
        FROM league_stats ls
        JOIN opp_stats os ON os.team_id = ls.team_id
    )
    SELECT *
    FROM ranked
    WHERE team_id = :team_id
    ''',
    params
).iloc[0]

n = int(ranked["league_size"])

logo_col, info_col, k1, k2, k3, k4 = st.columns([1, 2.3, 1, 1, 1, 1], vertical_alignment="center")

if league_id == "00":
    logo_col.image(f"https://cdn.nba.com/logos/nba/{team_id}/global/L/logo.svg")
else:
    logo_col.write("")

with info_col:
    st.markdown(
        f"<div style='font-size:30px; font-weight:700; margin-bottom:2px'>"
        f"{header['team_city']} {header['team_name']}</div>", unsafe_allow_html=True
    )
    st.markdown(
        f"<div style='font-size:14px; color:#9A9EA6; margin-bottom:6px;'>"
        f"{header['conference']}ern Conference | {header['division']} Division | "
        f"#{int(header['conf_rank'])} in conference | #{int(header['league_rank'])} overall</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<div style='font-size:16px; font-weight:600;'>"
        f"{int(header['wins'])}-{int(header['losses'])} ({header['win_pct']:.1%}) | "
        f"Last 10: {header['last_10_record']} | Streak: {header['current_streak']}</div>",
        unsafe_allow_html=True
    )

k1.metric("Offensive Rating", f"{ranked['offensive_rating']:.1f}")
k1.markdown(rank_badge_html(ranked['ortg_rank'], n), unsafe_allow_html=True)
k2.metric("Defensive Rating", f"{ranked['defensive_rating']:.1f}")
k2.markdown(rank_badge_html(ranked['drtg_rank'], n), unsafe_allow_html=True)
k3.metric("Net Rating", f"{ranked['net_rating']:.1f}")
k3.markdown(rank_badge_html(ranked['netrtg_rank'], n), unsafe_allow_html=True)
k4.metric("Pace", f"{ranked['pace']:.1f}")
k4.markdown(rank_badge_html(ranked['pace_rank'], n), unsafe_allow_html=True)

st.divider()

tab_overview, tab_season, tab_shooting, tab_roster, tab_games = st.tabs(['Overview', 'Season Trend', 'Shooting', 'Roster', 'Game Log'])

with tab_overview:
    st.caption("Four Factors - Offense")
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("eFG%", f"{ranked['efg_pct']:.1%}")
    f1.markdown(rank_badge_html(ranked['efg_rank'], n), unsafe_allow_html=True)
    f2.metric("TOV%", f"{ranked['tov_pct']:.1f}%")
    f2.markdown(rank_badge_html(ranked['tov_rank'], n), unsafe_allow_html=True)
    f3.metric("oREB%", f"{ranked['oreb_pct']:.1%}")
    f3.markdown(rank_badge_html(ranked['oreb_rank'], n), unsafe_allow_html=True)
    f4.metric("FTR", f"{ranked['ftr']:.1%}")
    f4.markdown(rank_badge_html(ranked['ftr_rank'], n), unsafe_allow_html=True)

    st.write("")
    st.caption("Four Factors - Defense")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Opp eFG%", f"{ranked['opp_efg_pct']:.1%}")
    d1.markdown(rank_badge_html(ranked['defg_rank'], n), unsafe_allow_html=True)
    d2.metric("Opp TOV%", f"{ranked['opp_tov_pct']:.1f}%")
    d2.markdown(rank_badge_html(ranked['dtov_rank'], n), unsafe_allow_html=True)
    d3.metric("dREB%", f"{ranked['dreb_pct']:.1%}")
    d3.markdown(rank_badge_html(ranked['dreb_rank'], n), unsafe_allow_html=True)
    d4.metric("Opp FTR%", f"{ranked['opp_ftr']:.1%}")
    d4.markdown(rank_badge_html(ranked['dftr_rank'], n), unsafe_allow_html=True)

with tab_season:
    st.markdown(
    '''
    <div style="display:flex; justify-content:center; align-items:center;margin-bottom:1rem;margin-left: 175px;">
        <h1 style="margin:0; font-size: 35px;">Season Performance</h1>
    </div>
    ''', unsafe_allow_html=True
    )
    window = st.select_slider("Rolling Window (games)", options=[5, 10, 15], value=10)

    trend = run_query(
        '''
        SELECT game_date, net_rating, wl
        FROM staging_marts.fct_team_games
        WHERE team_id = :team_id
            AND season = :season
            AND league_id = :league_id
            AND season_type = :season_type
        ORDER BY 1
        ''',
        params
    )
    trend["rolling_net_rating"] = trend['net_rating'].rolling(window=window, min_periods=1).mean()

    fig = go.Figure()

    # individual games colored by result
    fig.add_trace(go.Scatter(
        x=trend['game_date'], y=trend['net_rating'], mode="markers", name="Game Net Rating",
        marker=dict(size=6, opacity=0.4, color=trend["wl"].map({"W": "#5DCAA5", "L": "#E05C5C"})),
        hovertemplate="%{x|%b %d}: %{y:.1f}<extra></extra>"
    ))

    # rolling average
    fig.add_trace(go.Scatter(
        x=trend["game_date"], y=trend["rolling_net_rating"], mode="lines", name=f"{window}-game rolling avg",
        line=dict(color="#FF6B35", width=3), hovertemplate="%{x|%b %d}: %{y:.1f}<extra></extra>"
    ))

    # league average reference line
    fig.add_hline(y=0, line_dash="dash", line_color="#9A9EA6", opacity=0.6)

    fig.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117", 
        font=dict(color="#E8E8E8", family="Inter"),
        xaxis=dict(gridcolor="#2A2E37", title=None),
        yaxis=dict(gridcolor="#2A2E37", title="Net Rating"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=350, margin=dict(l=40, r=20, t=40, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

with tab_shooting:
    st.markdown(
        '''
        <div style="display:flex; justify-content:center; align-items:center;margin-bottom:1rem;margin-left: 175px;">
            <h1 style="margin:0; font-size: 35px;">Shot Distribution</h1>
        </div>
        ''', unsafe_allow_html=True
        )
    shot_zones = run_query(
        '''
        WITH team_zones AS (
            SELECT shot_zone_basic
                , SUM(fga) AS fga
                , SUM(fgm) AS fgm
            FROM staging_marts.fct_shot_zone_summary
            WHERE team_id = :team_id
                AND season = :season
                AND season_type = :season_type
                AND league_id = :league_id
            GROUP BY 1
        )
        , league_zones AS (
            SELECT shot_zone_basic 
                , SUM(fga) AS league_fga
                , SUM(fgm) AS league_fgm
            FROM staging_staging.stg_shot_zone_league_averages
            WHERE season = :season
                AND league_id = :league_id
                AND season_type = :season_type
            GROUP BY 1
        )
        SELECT tz.shot_zone_basic
            , tz.fga
            , tz.fgm::NUMERIC / NULLIF(tz.fga, 0) AS fg_pct
            , lz.league_fgm::NUMERIC / NULLIF(lz.league_fga, 0) AS league_fg_pct
            , (tz.fgm::NUMERIC / NULLIF(tz.fga, 0)) - (lz.league_fgm::NUMERIC / NULLIF(lz.league_fga, 0)) AS fg_pct_vs_league
        FROM team_zones tz
        LEFT JOIN league_zones lz ON lz.shot_zone_basic = tz.shot_zone_basic
        ORDER BY 2 DESC
        '''
        , params
    )
    fig2 = go.Figure(go.Bar(
        x=shot_zones["fga"], y=shot_zones["shot_zone_basic"], orientation="h",
        marker=dict(color=shot_zones["fg_pct_vs_league"], colorscale="RdYlGn", cmid=0, 
        showscale=True, colorbar=dict(title="vs League", tickformat=".0%")), customdata=shot_zones[['fg_pct', 'league_fg_pct']],
        hovertemplate="%{y}: %{x} attempts<br>Team FG%: %{customdata[0]:.1%}<br>League FG%: %{customdata[1]:.%}<extra></extra>"
    ))
    fig2.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="#E8E8E8", family="Inter"),
        xaxis=dict(gridcolor="#2A2E37", title="Attempts"),
        yaxis=dict(title=None),
        height=300, margin=dict(l=10, r=20, t=20, b=20)
    )
    st.plotly_chart(fig2, use_container_width=True)


with tab_roster:
    roster = run_query(
        '''
        SELECT DISTINCT tr.player_name, tr.jersey_number, tr.position, tr.height
            , tr.weight, tr.age, tr.player_exp, tr.how_acquired
        FROM staging_staging.stg_team_rosters tr 
        WHERE tr.team_id = :team_id
            AND tr.season = :season
        ORDER BY 1
        ''',
        {"team_id": team_id, "season": season}
    )

    st.dataframe(roster, hide_index=True, use_container_width=True, column_config={
        "player_name": st.column_config.TextColumn("Player"),
        "jersey_number": st.column_config.TextColumn("#"),
        "position": st.column_config.TextColumn("Pos"),
        "height": st.column_config.TextColumn("Ht"),
        "weight": st.column_config.NumberColumn("Wt"),
        "age": st.column_config.NumberColumn("Age"),
        "player_exp": st.column_config.TextColumn("Exp"),
        "how_acquired": st.column_config.TextColumn("Acquired"),
    })

    st.divider()
    st.markdown(
        '''
        <div style="display:flex; justify-content:center; align-items:center;margin-bottom:1rem;margin-left: 175px;">
            <h1 style="margin:0; font-size: 35px;">Player Usage vs Net Rating</h1>
        </div>
        ''', unsafe_allow_html=True
    )
    roster_players = run_query(
        '''
        SELECT player_id, player_name, usage, ROUND(net_rating::numeric, 2) AS net_rating, minutes_per_game, games_played
        FROM staging_marts.fct_player_season_summary
        WHERE team_id = :team_id
            AND season = :season
            AND season_type = :season_type
        '''
        , params
    )
    x_range = roster_players['usage'].max() - roster_players['usage'].min()
    y_range = roster_players['net_rating'].max() - roster_players['net_rating'].min()

    min_size_frac, max_size_frac = 0.05, 0.13
    mpg_min, mpg_max = roster_players['minutes_per_game'].min(), roster_players['minutes_per_game'].max()
    mpg_span = max(mpg_max-mpg_min, 1e-6)

    def size_frac(mpg):
        scaled = (mpg-mpg_min) / mpg_span 
        return min_size_frac + scaled * (max_size_frac - min_size_frac)

    fig_roster = go.Figure()
    fig_roster.add_trace(go.Scatter(
        x=roster_players['usage'], y=roster_players['net_rating'],
        mode='markers', marker=dict(size=1, opacity=0), text=roster_players['player_name'],
        customdata=roster_players[['minutes_per_game', 'games_played']],
        hovertemplate="%{text}<br>USG%: %{x:.1%}<br>Net Rtg: %{y:+.1f}<br>MIN: %{customdata[1]}<extra></extra>"
    ))

    for _, row in roster_players.iterrows():
        frac = size_frac(row['minutes_per_game'])
        fig_roster.add_layout_image(dict(
            source=f"https://cdn.nba.com/headshots/nba/latest/260x190/{row['player_id']}.png",
            x=row['usage'], y=row['net_rating'], xref='x', yref='y', sizex=x_range*frac, sizey=y_range*frac,
            xanchor="center", yanchor="middle", layer="above"
        ))

    fig_roster.add_vline(x=0.20, line_dash="dash", line_color="#9A9EA6", opacity=0.5, annotation_text="Avg Usage (20%)"
                         , annotation_font_color="#9A9EA6")
    fig_roster.add_hline(y=0, line_dash="dash", line_color="#9A9EA6", opacity=0.5)

    fig_roster.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="#E8E8E8", family="Inter", size=13),
        xaxis=dict(title="Usage Rate", gridcolor='#2A2E37', tickformat=".0%"),
        yaxis=dict(title="Net Rating", gridcolor="#2A2E37"),
        height=550, margin=dict(l=40, r=20, b=40)
    )

    st.plotly_chart(fig_roster, use_container_width=True)
with tab_games:
    games = run_query(
        '''
        SELECT game_date, matchup, wl, pts, opponent_pts
            , reb, ast, tov, stl, blk, fgm, fga, fg3m, fg3a, ftm, fta
            , offensive_rating, defensive_rating
        FROM staging_marts.fct_team_games
        WHERE team_id = :team_id
            AND league_id = :league_id 
            AND season = :season
            AND season_type = :season_type
        ORDER BY 1 DESC
        LIMIT 15
        ''',
        params
    )
    st.dataframe(games, hide_index=True, use_container_width=True, column_config={
        "game_date": st.column_config.DateColumn("Date"),
        "matchup": st.column_config.TextColumn("Matchup"),
        "wl": st.column_config.TextColumn("W/L"),
        "pts": st.column_config.NumberColumn("PTS"),
        "opponent_pts": st.column_config.NumberColumn("Opp PTS"),
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
        "offensive_rating": st.column_config.NumberColumn("Offensive Rating"),
        "defensive_rating": st.column_config.NumberColumn("Defensive Rating"),
    })