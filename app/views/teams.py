'''Team Profile Page'''

import numpy as np
import pandas as pd
import plotly.graph_objects as go 
import streamlit as st
from lib import charts, components as ui, filters, nav, queries, stats 

f = filters.current()
if f is None:
    ui.empty_state("No data yet.")
    st.stop()

all_teams = queries.team_seasons(f.season_type)
season_teams = all_teams[all_teams["season"] == f.season]
if season_teams.empty:
    ui.empty_state(f"No {f.season_type.lower()} data for {f.season}.", "Choose another season or season type above.")
    st.stop() 

pick_col, _ = st.columns([2, 3])
team = nav.team_picker(season_teams, pick_col)
team_id = str(team["team_id"])
n_teams = len(season_teams)
G = f.grain

def rank(key, df=season_teams):
    better = stats.get(key).better
    if better is None or key not in df:
        return None 
    r = df.set_index(df["team_id"].astype(str))[key].rank(ascending=not better, method="min")
    return int(r.loc[team_id]) if team_id in r.index and not pd.isna(r.loc[team_id]) else None

def ordinal(n):
    return f"{n}{'th' if 10 <=n % 100 <= 20 else {1:'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"

standings = queries.standings(f.season)
srow = standings[standings['team_id'].astype(str) == team_id]
subtitle = f"{int(team['wins'])}-{int(team['losses'])} in the {f.season_type.lower()}"
if len(srow) and f.season_type == "Regular Season":
    conf = srow.iloc[0]["conference"]
    conf_rank = (standings[standings["conference"] == conf].assign(wp=lambda d: d["wins"] / d["wins"] + d['losses']).sort_values("wp", ascending=False)["team_id"].astype(str).tolist().index(team_id) + 1)
    subtitle += f", {ordinal(conf_rank)} in the {conf}"

ui.page_header(team["team_name"], subtitle + ".", charts.team_logo_url(team_id))

prev = all_teams[(all_teams["season"] == f.previous_season) & (all_teams["team_id"].astype(str) == team_id)]
prev = prev.iloc[0] if len(prev) else None
cards = []
for key, label in (("offensive_rating", "Offensive Rating"), ("defensive_rating", "Defensive Rating"),
                   ("net_rating", "Net Rating"), ("pace", "Pace")):
    delta, good = ui.season_delta(key, team[key], prev[key] if prev is not None else None, f.previous_season)
    r = rank(key) if key != "pace" else int(season_teams.set_index(season_teams['team_id'].astype(str))["pace"].rank(ascending=False, method="min").loc[team_id])
    
    cards.append(ui.stat_card(label, stats.fmt(team[key], key), delta, good if key != "pace" else None))
ui.stat_cards(cards)
st.write("")

identity, style, shooting, roster, trends, games_tab = st.tabs(["Identity", "Style", "Shooting", "Roster", "Trends", "Games"])

with identity:
    st.caption("The Four Factors: shooting (eFG%), turnovers, offensive rebounding, and free throw rate.")
    lg_avg = season_teams.mean(numeric_only=True)

    def factor_rows(keys):
        rows = []
        for k in keys:
            r = rank(k)
            rows.append({"Factor": stats.label(k), "Team": stats.fmt(team[k], k), "League Average": stats.fmt(lg_avg[k], k),
                         "Rank": f"{ordinal(r)}" if r else "-",
                         "_good": None if r is None else 1 - (r - 1) / max(n_teams - 1, 1)})
        return pd.DataFrame(rows)

    def styled(df):
        colors = [charts.goodness_color(g) for g in df["_good"]]
        return (df.drop(columns="_good").style.apply(lambda _: [f"color: {c}; font-weight: 600" for c in colors], subset=["Rank"]))

    left, right = st.columns(2)
    with left:
        st.subheader("Offense")
        st.dataframe(styled(factor_rows(["efg_pct", "tov_pct", "oreb_pct", "ftr", "fg3pr", 'ts_pct'])), hide_index=True, width="stretch")
    with right:
        st.subheader("Defense")
        st.dataframe(styled(factor_rows(["opp_efg_pct", "opp_tov_pct", "dreb_pct", "opp_ftr", "opp_fg3pr", 'opp_ts_pct'])), hide_index=True, width="stretch")

    mix_keys = [("pts_paint", "Paint"), ("pts_fast_break", "Fast Break"), ("pts_2nd_chance", "Second chance"), ("pts_off_tov", "Off turnovers")]
    if f"{mix_keys[0][0]}_share" in team and not pd.isna(team.get(f"{mix_keys[0][0]}_share")):
        st.subheader("Points by Play Type Distribution")
        st.caption("Share of points scored, and allowed, by type; gray ticks are the league average.")
        fig = go.Figure()
        for prefix, name, color in (("", "Scored", charts.MAPLE), ("opp_", "Allowed", charts.ACCENT_2)):
            fig.add_trace(go.Bar(y=[m[1] for m in mix_keys], x=[team[f"{prefix}{m[0]}_share"] for m in mix_keys], name=name,
                                 orientation="h", marker_color=color, texttemplate="%{x:.1%}", textposition="outside", cliponaxis=False))

        fig.add_trace(go.Scatter(y=[m[1] for m in mix_keys], x=[lg_avg[f"{m[0]}_share"] for m in mix_keys], mode="markers",
                                 name="League Average", marker=dict(symbol="line-ns", size=26, line=dict(width=2, color=charts.MUTED))))
        fig.update_layout(barmode="group", height=320, xaxis=dict(tickformat=".0%", title="Share of points"),
                          yaxis=dict(autorange="reversed"), legend=dict(orientation="h", y=1.1, x=1, xanchor="right"))
        charts.show(fig, key="tp_mix")


with style:
    tpt = queries.team_play_types(f.season, f.season_type)
    mine = tpt[tpt['team_id'].astype(str) == team_id]
    if mine.empty:
        ui.empty_state("No play type data for this season.")
    else:
        left, right = st.columns(2)
        with left:
            st.subheader("Offense")
            st.caption("Share of possessions by play type; bar color represents the points per possessions compared to the league average")
            charts.show(charts.play_type_chart(mine[mine['type_grouping'] == "offensive"]), key="tp_pt_off")

        with right:
            st.subheader("Defense")
            st.caption("Share of opponent possessions by play type; bar color represents the points allowed per possession compared to the league average")
            charts.show(charts.play_type_chart(mine[mine['type_grouping'] == "defensive"], defensive=True), key="tp_pt_def")
        table = mine.copy()
        table['side'] = table['type_grouping'].str.capitalize()
        table = table.sort_values(['side', 'frequency'], ascending=[False, False])
        ui.data_table(table, ['side', 'play_type_label', 'possessions', 'frequency', 'ppp', 'league_ppp', 'ppp_rank'],
                      labels={'side': 'Side', 'play_type_label': 'Play type', "ppp": "PPP"
                              , 'league_ppp': "League Avg PPP", "ppp_rank": f"Rank out of {n_teams} Teams"})


with shooting:
    zones = queries.shot_zones(f.season, f.season_type, team_id=team_id)
    shots = queries.shots(f.season, f.season_type, team_id=team_id)
    if zones.empty:
        ui.empty_state("No shot data for this season.")
    else:
        left, right = st.columns([5, 4])
        with left:
            st.subheader("Shot Zone Frequencies")
            st.caption(f"{len(shots):,} field goal attempts; brighter areas are more frequent.")
            # Counts on a 2 ft grid, square-rooted so the rim does not drown out other areas.
            H, xe, ye = np.histogram2d(shots['loc_x'], shots['loc_y'], bins=[np.arange(-250, 251, 20), np.arange(-50, 311, 20)])
            fig = go.Figure(go.Heatmap(
                x=(xe[:-1] + xe[1:]) / 2, y=(ye[:-1] + ye[1:]) / 2, z=np.sqrt(H.T), zsmooth="best", showscale=False,
                colorscale=[[0, "rgba(14,23,38,0)"], [0.08, "rgba(226, 166, 90, 0.10)"], [0.5, "rgba(226,166,90,0.55)"],
                                                      [1, "rgba(226,166,90,0.95)"]], hoverinfo="skip"))
            charts.draw_court(fig, color=charts.MUTED)
            fig.update_layout(height=460, showlegend=False, margin=dict(l=0, r=0, t=8, b=0))
            charts.show(fig, key="tp_density")

        with right:
            st.subheader("Efficiency by zone")
            st.caption("Team FG% from each zone minus the league average.")
            charts.show(charts.zone_chart(zones), key="tp_zones")


with roster:
    by_team = queries.player_seasons_by_team(f.season, f.season_type)
    players = by_team[by_team['team_id'].astype(str) == team_id].sort_values("total_minutes", ascending=False)
    oo = queries.player_on_off(f.season, f.season_type)
    oo = oo[oo["team_id"].astype(str) == team_id][["player_id", "net_rating_diff", "possessions_on", "possessions_off"]]
    players = players.merge(oo, on="player_id", how="left")
    if players.empty:
        ui.empty_state("No players for this team and season.")
    else:
        st.caption("Player stats for their time on the team")
        left, right = st.columns([3, 2])
        with left:
            picked = ui.data_table(players, ["player_name", "position", "games_played", "minutes_per_game", stats.column("pts", G),
                                            stats.column("reb", G), stats.column("ast", G), "ts_pct", "usage", "net_rating_diff"],
                                            labels={"player_name": "Player", "position": "Pos", "net_rating_diff": "On/off"},
                                            selectable=True, key="tp_roster", height=460)
            if picked is not None:
                nav.open_player(players.loc[picked, "player_id"])
        with right:
            st.subheader("Role and Impact")
            st.caption("Usage lined up with team's net rating with each player on compared to off. Dot size is minutes" \
            " (Players with <300 minutes are left out)")
            d = players[(players['total_minutes'] >= 300) & players["net_rating_diff"].notna()]
            fig = go.Figure(go.Scatter(
                x=d["usage"], y=d["net_rating_diff"], mode="markers+text", text=d["player_name"].str[0] + ". " + d['player_name'].str.split().str[-1],
                textposition="top center", textfont=dict(color=charts.MUTED, size=11),
                marker=dict(size=d["total_minutes"] / d["total_minutes"].max() * 26 + 6 if len(d) else 8,
                            color=[charts.goodness_color(charts.diff_goodness(v, True, 8)) for v in d["net_rating_diff"]],
                            line=dict(width=1, color=charts.NAVY)),
                            customdata=d["player_name"], hovertemplate="%{customdata}<br>USG %{x:.1%}, on/off %{y:+.1f}<extra></extra>"))
            fig.add_hline(y=0, line_color=charts.MUTED, line_width=1, line_dash="dot")
            fig.update_layout(height=420, xaxis=dict(title="Usage", tickformat=".0%"), yaxis=dict(title="On/off net rating"))
            charts.show(fig, key="tp_impact")


with trends:
    history = all_teams[all_teams["team_id"].astype(str) == team_id].sort_values("season")
    league = queries.league_seasons(f.season_type)
    if len(history) < 2:
        st.caption("Only one season of data is in the DB.")
    st.caption("This team's stats across seasons; the dotted line is the league average, if applicable")
    keys = ["offensive_rating", "defensive_rating", "net_rating", "pace", "efg_pct", "fg3pr", "ftr", "tov_pct",  "oreb_pct", "dreb_pct"]
    cols = st.columns(2)
    for i, key in enumerate(keys):
        with cols[i % 2]:
            charts.show(charts.trend_chart(history, key, f.seasons, highlight=f.season, league=league if key in league else None),
                        key=f"tp_trend{key}")


with games_tab:
    games = queries.team_games(team_id, f.season, f.season_type)
    if games.empty:
        ui.empty_state("No games logged for this season.")
    else:
        if "net_rating" not in games and {"offensive_rating", "defensive_rating"} < set(games):
            games["net_rating"] = games["offensive_rating"] - games["defensive_rating"]
        opp_pts = next((c for c in ('opponent_pts', "opp_pts") if c in games), None)
        if "net_rating" in games:
            st.caption("Team's net rating for each game with rolling 10-game average depicted in maple.")
            charts.show(charts.game_trend(games, "net_rating"), key="tp_game_trend")
        log = games.sort_values("game_date", ascending=False).copy()
        log["Date"] = pd.to_datetime(log['game_date']).dt.strftime("%b %d")
        opp_name = next((c for c in ("opponent_team_name", "opponent_name", "matchup") if c in log), None)
        log["Opponent"] = log[opp_name] if opp_name else ""
        if "home_away" in log:
            log["Opponent"] = log["home_away"].map({"Home": "vs ", "Away": "at "}).fillna("") + log["Opponent"]
        log["Result"] = log["win_flag"].map({1: "W", 0: "L"})
        if opp_pts:
            log["Score"] = log["pts"].astype(int).astype(str) + "-" + log[opp_pts].astype(int).astype(str)
        cols = [c for c in ["Date", "Opponent", "Result", "Score", "offensive_rating", "defensive_rating", "net_rating"] if c in log]
        config = {k: st.column_config.NumberColumn(stats.label(k), format="%+.1f" if k == "net_rating" else "%.1f")
                  for k in ("offensive_rating", "defensive_rating", "net_rating") if k in cols}
        st.dataframe(log[cols], hide_index=True, width="stretch", column_config=config, height=420)