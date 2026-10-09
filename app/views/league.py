'''
League overview: The baseline statistics/trends that defined this season, and how they compare from previous/future seasons.
'''
import streamlit as st
from lib import charts, components as ui, filters, nav, queries, stats 

f = filters.current()
if f is None:
    ui.empty_state("No data in db :(")
    st.stop() 

league = queries.league_seasons(f.season_type)
now = league[league['season'] == f.season]
if now.empty:
    ui.empty_state(f"No {f.season_type.lower()} data for {f.season}.", "Try another season or season type above.")
    st.stop()
now = now.iloc[0]
prev = league[league['season'] == f.previous_season]
prev = prev.iloc[0] if len(prev) else None 

ui.page_header(f"The {f.season} season", f"{f.season_type}")

KPIS = [("pace", "Pace"), ("offensive_rating", "Points per 100 possessions"), ('fg3pr', "Rate of three point attempts"),
        ("ts_pct", "True shooting efficiency")]
cards = []
for key, label in KPIS:
    delta, _ = ui.season_delta(key, now[key], prev[key] if prev is not None else None, f.previous_season)
    cards.append(ui.stat_card(label, stats.fmt(now[key], key), delta, None))
ui.stat_cards(cards)

if len(league) > 1:
    st.subheader("The Decade So Far")
    st.caption(f"League averages for every {f.season_type.lower()} in the data; {f.season} in maple.")
    cols = st.columns(4)
    for col, (key, _) in zip(cols, KPIS):
        with col:
            charts.show(charts.trend_chart(league, key, f.seasons, highlight=f.season, height=220), key=f"lg_trend_{key}")

teams = queries.team_seasons(f.season_type)
teams = teams[teams['season'] == f.season]
tab_teams, tab_standings, tab_styles, tab_leaders = st.tabs(["Team Efficiency", "Standings", "Play Styles", "Leaders"])

with tab_teams:
    st.caption("Each team's offensive and defensive ratings. ")
    event = st.plotly_chart(charts.team_landscape(teams), theme=None, width="stretch", key="lg_landscape",
                            on_select="rerun", selection_mode="points")
    points = event.selection.points if event and event.selection else []
    if points:
        nav.open_team(points[0]['customdata'])

with tab_standings:
    standings = queries.standings(f.season)
    if standings.empty:
        ui.empty(f"No standings for {f.season}.")
    else:
        rs = queries.team_seasons("Regular Season")
        rs = rs[rs["season"] == f.season][["team_id", "net_rating", "offensive_rating", "defensive_rating"]]
        s = standings.merge(rs, on="team_id", how="left")
        s["win_pct"] = s["wins"] / (s["wins"] + s["losses"])
        s["logo"] = s["team_id"].map(charts.team_logo_url)
        s["name"] = s["team_city"].fillna('') + " " + s["team_name"].fillna("")
        st.caption("Regular season standings. Click a team to open its page.")
        cols = st.columns(2)
        for col, conf, title in ((cols[0], "East", "Eastern Conference"), (cols[1], "West", "Western Conference")):
            c = s[s["conference"] == conf].sort_values("win_pct", ascending=False).reset_index(drop=True)
            if c.empty:
                continue 
            lead = c.iloc[0]
            c["gb"] = ((lead["wins"] - c["wins"]) + (c["losses"] - lead["losses"])) / 2 
            c["seed"] = range(1, len(c) + 1)
            with col:
                st.subheader(title)
                event = st.dataframe(
                    c[["seed", "logo", "name", "wins", "losses", "win_pct", "gb", "offensive_rating", "defensive_rating", "net_rating"]], 
                    hide_index=True, width="stretch", on_select="rerun", selection_mode="single-row", key=f"lg_standings_{conf}",
                    column_config={
                        "seed": st.column_config.NumberColumn("", width="small"),
                        "logo": st.column_config.ImageColumn("", width="small"),
                        "name": st.column_config.TextColumn("Team"),
                        "wins": st.column_config.NumberColumn("W", format="%d"),
                        "losses": st.column_config.NumberColumn("L", format="%d"),
                        "win_pct": st.column_config.NumberColumn("Win%", format="%.3f"),
                        "gb": st.column_config.NumberColumn("GB", format="%.1f"),
                        "offensive_rating": st.column_config.NumberColumn("Offensive Rating", format="%+.1f",
                                                                                            help=stats.get("offensive_rating").desc),
                        "defensive_rating": st.column_config.NumberColumn("Defensive Rating", format="%+.1f",
                                                                                            help=stats.get("defensive_rating").desc),
                        "net_rating": st.column_config.NumberColumn("Net Rating", format="%+.1f",
                                                                    help=stats.get("net_rating").desc)
                    }
                )
                if event.selection.rows:
                    nav.open_team(c.iloc[event.selection.rows[0]]["team_id"])

with tab_styles:
    tpt = queries.team_play_types(f.season, f.season_type)
    off = tpt[tpt["type_grouping"] == "offensive"]
    if off.empty:
        ui.empty_state(f"No play type data for {f.season}.")
    else:
        mix = off.groupby(["play_type", "play_type_label"]).agg(possessions=("possessions", "sum"), pts=("pts", "sum")).reset_index()
        mix["frequency"] = mix["possessions"] / mix["possessions"].sum()
        mix["ppp"] = mix["pts"] / mix["possessions"]
        mix["league_ppp"] = (mix["pts"].sum() / mix["possessions"].sum())
        mix["ppp_vs_league"] = mix["ppp"] - mix["league_ppp"]
        left, right = st.columns([3, 2])
        with left:
            st.subheader("League Play Type Overview")
            st.caption("Share of all posssessions by play type. The bar color compares each play's points" \
            " per possession " f"with the league's {mix['league_ppp'].iloc[0]:.2f}: blue plays are more efficient than average.")
            charts.show(charts.play_type_chart(mix, min_poss=0), key="lg_mix")
        with right:
            st.subheader("Team Play Type Overview")
            pt_choice = st.selectbox("Play type", mix.sort_values("frequency", ascending=False)["play_type"].tolist(),
                                     format_func=dict(zip(mix["play_type"], mix["play_type_label"])).get, key="lg_pt")
            t = off[off["play_type"] == pt_choice].sort_values("frequency", ascending=False)
            ui.data_table(t, ["team_name", "frequency", "ppp", "ppp_rank"],
                          labels={"team_name": "Team", "ppp_rank": "PPP Rank"})


with tab_leaders:
    G = f.grain
    everyone = queries.player_seasons(f.season_type)
    everyone = everyone[everyone['season'] == f.season]
    if everyone.empty:
        ui.empty_state(f"No player stats for the {f.season} {f.season_type.lower()} yet.")
    else:
        c1, c2, c3 = st.columns([1.3, 2, 1.7])
        qualified = c1.toggle("Qualified Players Only", value=True, key="lg_lead_qual",
                              help="Players who meet the games and minutes thresholds for the season.")
        groups = c2.multiselect("Positions", ["Guard", "Forward", "Center"], default=["Guard", "Forward", "Center"],
                                key="lg_lead_pos")
        team = c3.selectbox("Team", ["All Teams"] + sorted(everyone["last_team_name"].dropna().unique()), key="lg_lead_team")

        players = everyone[everyone["position_group"].isin(groups)]
        if qualified:
            players = players[players['is_eligible']]
        if team != "All Teams":
            players = players[players['last_team_name'] == team]

        BASE = ["player_name", 'last_team_name']
        BASE_LABELS = {"player_name": "Player", "last_team_name": "Team"}

        def board(frame, cols, sort_by, key, labels=None):
            if frame.empty:
                ui.empty_state("No players match these filters.", "Loosen the position, team, or qualified filters.")
                return 
            frame = frame.sort_values(sort_by, ascending=stats.get(sort_by).better is False,
                                      na_position="last").reset_index(drop=True)
            picked = ui.data_table(frame, BASE + cols, labels={**BASE_LABELS, **(labels or {})}, selectable=True,
                                   key=key, height=min(38 * len(frame) + 40, 640), pinned=["player_name"])

            if picked is not None:
                nav.open_player(frame.loc[picked, "player_id"])

        st.caption(f"{len(players)} players, counting stats {stats.GRAIN_LABELS[G].lower()}. Click a column header to "
                   "sort by it, or a row to opent the player's profile.")
        general, advanced, tracking = st.tabs(["General", "Advanced", "Tracking"])

        with general:
            c = lambda *keys: [stats.column(k, G) for k in keys]
            cols = (["games_played", "minutes_per_game"] + c("pts", "fgm", "fga") + ["fg_pct"]
                    + c("fg2m", "fg2a") + ["fg2_pct"] + c("fg3m", "fg3a") + ["fg3_pct"] + c("ftm", "fta") + ["ft_pct"]
                    + c("oreb", "dreb", "reb", "ast", "stl", "blk", "tov", "pf", "plus_minus"))
            board(players, cols, stats.column("pts", G), "lg_lead_general")

        with advanced:
            st.caption("Ratings are the team's points scored and allowed per 100 possessions while the player is on the court. "
                       "Hover over a column header for its definition.")
            cols = ["games_played", "minutes_per_game", "offensive_rating", "defensive_rating", "net_rating", "ts_pct",
                    "relative_ts_pct", "efg_pct", "usage", "oreb_pct", "dreb_pct", "reb_pct", "assist_pct", "ast_to_tov",
                    "tov_pct", "stl_pct", "blk_pct"]
            board(players, cols, "net_rating", "lg_lead_advanced")


        with tracking:
            CATEGORIES = {
                "Catch & Shoot":(["catch_shoot_fgm", "catch_shoot_fga"], ["catch_shoot_fg_pct"],
                                 ["catch_shoot_fg3m", "catch_shoot_fg3a"], ["catch_shoot_fg3_pct", "catch_shoot_efg"],
                                 ["catch_shoot_pts"]),

                "Pull Ups": (["pullup_fgm", "pullup_fga"], ["pullup_fg_pct"],
                             ["pullup_fg3m", "pullup_fg3a"], ["pullup_fg3_pct", "pullup_efg_pct"],
                            ["pullup_pts"]),

                "Drives": (["drives", "drive_fgm", "drive_fga"], ["drive_fg_pct"], ["drive_pts", "drive_ast", "drive_tov"]),

                "Post Ups": (["post_touches", "post_touch_fgm", "post_touch_fga"], ["post_touch_fg_pct"],
                              ["post_touch_pts", "post_touch_ast", "post_touch_tov"]),

                "Shot Creation": ([], ["pct_ast_fgm", "pct_uast_fgm", "pct_ast_3pm", "pct_uast_3pm", "pct_uast_2pm", "pct_pts_paint"])
            }
            category = st.segmented_control("Category", list(CATEGORIES), default="Catch & Shoot", key="leg_lead_trk_cat",
                                            label_visibility="collapsed") or "Catch & Shoot"
            trk = queries.player_tracking(f.season, f.season_type, G)
            if trk.empty:
                ui.empty_state(f"No tracking data for the {f.season} {f.season_type.lower()}.")
            else:
                cols = [stats.column(k, G) if stats.get(k).scaled else k for group in CATEGORIES[category] for k in group]
                frame = players[["player_id", "player_name", "last_team_name", "games_played", "minutes_per_game"]].merge(
                    trk[["player_id"] + [k for k in cols if k in trk]], on="player_id", how="inner")
                cols = [k for k in cols if k in frame]
                short = {k: stats.label(k).replace(f"{prefix} ", "") for k in cols
                         for prefix in ("Catch & Shoot", "Pull Up", "Drive", "Post Up") if stats.label(k).startswith(prefix)}
                sort_by = next((k for k in cols if k.endswith(f"_pts_{G}")), cols[0])
                board(frame, ["games_played", "minutes_per_game"] + cols, sort_by, "lg_lead_tracking", labels=short)