'''Player Profile Page''' 

import pandas as pd
import streamlit as st 
from lib import charts, components as ui, filters, nav, queries, stats
from lib.percentiles import add_percentiles

f = filters.current()

if f is None:
    ui.empty_state("No data yet")
    st.stop()

all_seasons = queries.player_seasons(f.season_type)
season_df = all_seasons[all_seasons["season"] == f.season]
if season_df.empty:
    ui.empty_state(f"No {f.season_type.lower()} data for {f.season}.", "Choose another season or season type above.")
    st.stop()

pick_col, _ = st.columns([2, 3])
player, missing = nav.player_picker(season_df, pick_col)
player_id = player["player_id"]
if missing: 
    played = sorted(all_seasons.loc[all_seasons["player_id"] == missing, "season"].unique())
    name = all_seasons.loc[all_seasons["player_id"] == missing, "player_name"]
    if len(name):
        st.info(f"{name.iloc[0]} has no {f.season_type.lower()} games in {f.season}" + \
        (f"; he played in {', '.join(played)}." if played else ".") + " Showing the season's minutes leader instead.")

G = f.grain 

bio = queries.player_bio(player_id)
by_team = queries.player_seasons_by_team(f.season, f.season_type)
teams_this_season = by_team.loc[by_team["player_id"] == player_id].sort_values("total_minutes", ascending=False)["team_name"].tolist()

def bio_line(bio, row):
    parts = []
    pos = row.get("position") or (bio.get("position") if bio is not None else None)
    team_text = " and ".join(teams_this_season) if teams_this_season else row.get("last_team_name")
    parts.append(f"{pos} for the {team_text}" if pos else str(team_text))
    if bio is not None:
        if bio.get("height") and not pd.isna(bio.get("weight")):
            parts.append(f"{bio['height']}, {int(bio['weight'])} lbs")
        if bio.get("birthdate") is not None and not pd.isna(bio.get("birthdate")):
            season_end = pd.Timestamp(f"20{f.season[-2:]}-02-01")
            parts.append(f"age {int((season_end - pd.Timestamp(bio['birthdate'])).days // 365.25)} that season")
        dy = str(bio.get("draft_year") or "")
        if dy.isdigit():
            parts.append(f"{dy} draft, round {bio.get('draft_round')}, pick {bio.get('draft_number')}")
        elif dy:
            parts.append("undrafted")
    return ". ".join(p[0].upper() + p[1:] for p in parts if p) + "."

ui.page_header(player['player_name'], bio_line(bio, player), charts.headshot_url(player_id))
if not player['is_eligible']:
    st.caption(f"{int(player['games_played'])} games at {player['minutes_per_game']:.1f} minutes is below the qualifiying "
               "threshold, so he isn't in the percentile pools. His percentiles below are compared to qualifiying players.")

SCORING = ["pts", "ts_pct", "relative_ts_pct", "efg_pct", "fg3_pct", "ft_pct", "fg3pr", "ftr", "usage"]
PLAYMAKING = ["ast", "assist_pct", "tov_pct", "reb", "oreb_pct", "dreb_pct"]
DEFENSE = ["stl", "blk", "stl_pct", "blk_pct", "defensive_rating"]
pct_keys = SCORING + PLAYMAKING + DEFENSE + ["net_rating"]
pct_cols = [stats.column(k, G) for k in pct_keys]

with_pctiles = add_percentiles(season_df, pct_cols)
me = with_pctiles.set_index("player_id").loc[player_id]
prev = all_seasons[(all_seasons["season"] == f.previous_season) & (all_seasons["player_id"] == player_id)]
prev = prev.iloc[0] if len(prev) else None

cards = []
for key in ["pts", "reb", "ast", "ts_pct", "usage", "net_rating"]:
    col = stats.column(key, G)
    delta, good = ui.season_delta(col, me[col], prev[col] if prev is not None else None, f.previous_season)
    pctile = me.get(f"{col}_pctile")
    note = f"{round(pctile * 100)}th percentile" if pctile is not None and not pd.isna(pctile) else None
    label = stats.label(key) + ("" if not stats.get(key).scaled else f" {stats.GRAIN_LABELS[G].lower()}")
    cards.append(ui.stat_card(label, stats.fmt(me[col], key), delta, good, note))
ui.stat_cards(cards)
st.write('')

overview, scoring, defense, impact, trends, gamelog = st.tabs(["Overview", "Scoring", "Defense", "Impact", "Trends", "Game Log"])

with overview:
    group = player.get("position_group") if isinstance(player.get('position_group'), str) else None 
    by_pos = st.toggle(f"Compare with {group.lower()}s only" if group else "Compare within position")
    pool = add_percentiles(season_df, pct_cols, group_col="position_group") if by_pos else with_pctiles 
    r = pool.set_index("player_id").loc[player_id]
    pool_size = int(season_df['is_eligible'].sum() if not by_pos else 
                    season_df.loc[season_df['position_group'] == group, 'is_eligible'].sum())
    st.caption(f"Percentile against {pool_size} qualified players {'players' if not by_pos else group.lower() + 's'} in "
               f"{f.season}. Counting stats are {stats.GRAIN_LABELS[G].lower()}.")

    c1, c2, c3 = st.columns(3)
    for col, title, keys in ((c1, "Scoring and Shooting", SCORING), (c2, "Playmaking and Rebounding", PLAYMAKING),
                             (c3, "Defense", DEFENSE)):
        with col:
            st.subheader(title)
            ui.percentile_bars([(stats.column(k, G), r[stats.column(k, G)], r.get(f"{stats.column(k, G)}_pctile")) for k in keys])


with scoring:
    shots = queries.shots(f.season, f.season_type, player_id=player_id)
    zones = queries.shot_zones(f.season, f.season_type, player_id=player_id)
    left, right = st.columns([5, 4])
    with left:
        st.subheader("Shot Chart")
        if shots.empty:
            ui.empty_state("No shot locations for this season.")
        else:
            made = int(shots['shot_made_flag'].sum())
            st.caption(f"{made} of {len(shots)} field goals ({made / len(shots):.1%}).")
            charts.show(charts.shot_chart(shots), key='pp_shots')

    with right:
        st.subheader("Efficiency by Shot Zone")
        if zones.empty:
            ui.empty_state("No zone data for this season.")
        else:
            st.caption("FG% from each zone minus the league average FG% from the same spot.")
            charts.show(charts.zone_chart(zones), key="pp_zones")

    st.subheader("Scoring Play Types")
    ptypes = queries.player_play_types(f.season, f.season_type)
    mine = ptypes[(ptypes["player_id"] == player_id) & (ptypes["type_grouping"] == "offensive")]
    tracking = queries.player_tracking(f.season, f.season_type, G)
    trk = tracking[tracking['player_id'] == player_id]
    left, right = st.columns([5, 4])
    with left:
        if mine.empty:
            ui.empty_state("No play type data for this season.")
        else:
            st.caption("Share of player's possessions by play type. The bar color indicates their points per possession compared "
                       "to the league average on the same play type. Green is better. Play types with under 10 total possessions are excluded.")
            charts.show(charts.play_type_chart(mine), key="pp_playtypes")

    with right:
        if trk.empty:
            ui.empty_state("No shot type data for this season.")
        else:
            t = trk.iloc[0]
            g_label = stats.GRAIN_LABELS[G].lower()
            rows = [
                ("Catch and shoot", f"{t[f'catch_shoot_fga_{G}']:.1f} attempts {g_label}", f"{t['catch_shoot_efg']:.1%} eFG%"),
                ("Pull Ups", f"{t[f'pullup_fga_{G}']:.1f} attempts {g_label}", f"{t['pullup_efg_pct']:.1%} eFG%"),
                ("Drives", f"{t[f'drives_{G}']:.1f} drives {g_label}", f"{t[f'drive_pts_{G}']:.1f} points"),
                ("Post Ups", f"{t[f'post_touches_{G}']:.1f} touches {g_label}", f"{t[f'post_touch_pts_{G}']:.1f} points"),
                ("Assisted/Unassisted Baskets", f"{t[f'pct_ast_fgm']:.0%} assisted", f"{t['pct_uast_fgm']:.0%} unassisted"),
                ("Paint Scoring", f"{t[f'pct_pts_paint']:.0%} of his points", "")
            ]
            st.caption("Shot type data from player tracking.")
            st.dataframe(pd.DataFrame(rows, columns=["Type", "Volume", "Result"]), hide_index=True, width="stretch")

with defense:
    dfn_all = queries.player_defense(f.season_type)
    dfn = dfn_all[dfn_all["season"] == f.season].merge(season_df[["player_id", "is_eligible"]], on="player_id", how="left")
    mine = dfn[dfn["player_id"] == player_id]
    if mine.empty:
        ui.empty_state("No defensive tracking data for this season.")
    else:
        d = mine.iloc[0]
        cards = []
        for prefix, label in (('overall', 'All shots defended'), ("rim", "At the rim (within 6 ft)"), ("fg3", "Three Pointers")):
            diff = d[f"{prefix}_fg_pct_diff"]
            cards.append(ui.stat_card(f"Opponent FG%, {label.lower()}", stats.fmt(d[f"{prefix}_d_fg_pct"], format_code="pct"),
                                      f"{stats.fmt(diff, format_code='pct_pts')} vs expected", None if pd.isna(diff) or diff == 0 else diff < 0,
                                      f"{int(d[f'{prefix}_d_fga'])} shots defended"))

        ui.stat_cards(cards)
        left, right = st.columns(2)
        with left:
            st.subheader("Opponent Shooting by Distance")
            st.caption("Opponents' FG% with him as the closest defender compared to what the opponent's usual FG% from there.")
            cats =[("overall", "All shots"), ("fg2", "Twos"), ("fg3", "Threes"), ("rim", "Within 6 Ft"), ("lt_10ft", "Within 10 Ft"),
                   ("gt_15ft", "Beyond 15 Ft")]
            charts.show(charts.dot_compare([c[1] for c in cats], [d[f"{c[0]}_d_fg_pct"] for c in cats],
                                           [d[f"{c[0]}_normal_fg_pct"] for c in cats], "fg_pct"), key="pp_dfg")
        with right:
            st.subheader("Hustle Stats Per 36 Minutes")
            hustle = ["deflections_per_36", "contested_shots_per_36", "loose_balls_recovered_per_36",
                      "charges_drawn_per_36", "boxouts_per_36", "screen_assists_per_36"]
            hp = add_percentiles(dfn, hustle).set_index("player_id").loc[player_id]
            st.caption("Percentiles in comparison to qualified players this season.")
            ui.percentile_bars([(k, hp[k], hp.get(f"{k}_pctile")) for k in hustle])
        dtypes = ptypes[(ptypes['player_id'] == player_id) & (ptypes['type_grouping'] == "defensive")]
        if not dtypes.empty:
            left, _ = st.columns([3, 2])
            with left:
                st.subheader("Defended Play Types")
                st.caption("Share of possessions he defends by play type. Bar color is points allowed per possession "
                           "in comparison to the league average")
                
                charts.show(charts.play_type_chart(dtypes, defensive=True), key="pp_def_playtypes")

with impact:
    oo_all = queries.player_on_off(f.season, f.season_type)
    oo = oo_all[oo_all["player_id"] == player_id]
    if oo.empty:
        ui.empty_state("No on/off data for this season.")
    else:
        if len(oo) > 1:
            team_names = dict(zip(by_team['team_id'].astype(str), by_team['team_name']))
            team_choice = st.segmented_control("Team", oo["team_id"].astype(str).tolist(), format_func=lambda t: team_names.get(t, t),
                                               default=str(player['last_team_id']), key="pp_onoff_team")
            row = oo[oo["team_id"].astype(str) == (team_choice or str(player['last_team_id']))].iloc[0]
        else:
            row = oo.iloc[0]
        oo_pct = add_percentiles(oo_all.merge(season_df[['player_id', 'is_eligible']], on="player_id", how="left"),
                                 ["net_rating_diff"])
        np_ = oo_pct.loc[(oo_pct["player_id"] == player_id) & (oo_pct["team_id"]), "net_rating_diff_pctile"]
        cards = [
            ui.stat_card("Team Net Rating When On Court", stats.fmt(row["on_net_rating"], "net_rating"),
                         note=f"{row['possessions_on']:,.0f} possessions"),
            ui.stat_card("Team Net Rating When Off", stats.fmt(row["off_net_rating"], "net_rating"),
                                     note=f"{row['possessions_off']:,.0f} possessions"),
            ui.stat_card("On/Off Swing", stats.fmt(row["net_rating_diff"], "net_rating"),
                        None, None, f"{round(np_.iloc[0] * 100)}th percentile" if len(np_) and not pd.isna(np_.iloc[0]) else None),
            ui.stat_card("Share of Team Minutes", stats.fmt(row["on_court_share"], format_code="pct"))
        ]
        ui.stat_cards(cards)
        st.write("")
        if row["possessions_off"] < 1000:
            st.warning(f"*Only {row['possessions_off']:,.0f} possessions without player.*")
        st.caption("Each row is the team's number with him off the court (gray) and on it (maple). The line is "
                   "green when the team has been better with him on")

        left, right = st.columns(2)
        with left:
            st.subheader("Offense")
            charts.show(charts.on_off_chart(row, ["offensive_rating", "efg_pct", "tov_pct", "oreb_pct", "fg3pr", "ftr", "pace"]), key="pp_oo_off")
        with right:
            st.subheader("Defense")
            charts.show(charts.on_off_chart(row, ["defensive_rating", "opp_efg_pct", "opp_tov_pct", 
                                                  "dreb_pct", "opp_fg3pr", "opp_ftr", "net_rating"]), key="pp_oo_def")

with trends:
    history = all_seasons[all_seasons["player_id"] == player_id].sort_values("season")
    league = queries.league_seasons(f.season_type)
    if len(history) < 2:
        st.caption(f"Only one {f.season_type.lower()} season so far, so no season-over-season trend to show.")
    st.caption("Hollow points are seasons below the qualifiying threshold; gaps are seasons they didn't play.")
    defaults = [stats.column("pts", G), "ts_pct", "usage", "net_rating"]
    c1, c2 = st.columns(2)
    for i, key in enumerate(defaults):
        with (c1 if i % 2 == 0 else c2):
            charts.show(charts.trend_chart(history, key, f.seasons, highlight=f.season,
                                            league=league if key in league else None), key=f"pp_trend_{key}")

    TREND_CHOICES = [stats.column(k, G) for k in ["reb", "ast", "stl", "blk", "tov"]] + [
        "minutes_per_game", "efg_pct", "fg3_pct", "ft_pct", "fg3pr", "ftr", "relative_ts_pct", "assist_pct",
        "tov_pct", "reb_pct", "stl_pct", "blk_pct", "offensive_rating", "defensive_rating"
    ]
    pick = st.selectbox("Another stat", TREND_CHOICES, format_func=lambda k: stats.label(k), key="pp_trend_pick")
    charts.show(charts.trend_chart(history, pick, f.seasons, highlight=f.season, league=league if pick in league else None),
                key="pp_trend_custom")
    table = history.sort_values("season", ascending=False).copy()
    table["team"] = table["last_team_name"] + table["teams_played_for"].map(lambda n: f" ({int(n)} teams)" if n > 1 else "")
    ui.data_table(table, ["season", "team", "games_played", "minutes_per_game", stats.column('pts', G), stats.column("reb", G),
                            stats.column("ast", G), "ts_pct", "usage", "net_rating"], labels={"season": "Season", "team": "Team"})


with gamelog:
    games = queries.player_games(player_id, f.season, f.season_type)
    if games.empty:
        ui.empty_state("No games logged for this season.")
    else:
        choices = {k: k for k in ["pts", "reb", "ast", "minutes", "ts_pct"] if k in games}
        pick = st.segmented_control("Stat", list(choices), format_func=lambda k: "MIN" if k == "minutes" else stats.label(k),
                                    default="pts", key="pp_game_stat") or "pts"
        charts.show(charts.game_trend(games, pick), key="pp_game_trend")
        log = games.sort_values("game_date", ascending=False).copy()
        log["Date"] = pd.to_datetime(log['game_date']).dt.strftime("%b %d")
        log["Game"] = log["matchup"] if "matchup" in log else log["team_name"]
        log["Result"] = log["win_flag"].map({1: "W", 0: "L"}) if "win_flag" in log else ""
        for made, att, label in (("fgm", "fga", "FG"), ("fg3m", "fg3a", "3P"), ("ftm", "fta", "FT")):
            if made in log and att in log:
                log[label] = log[made].astype(int).astype(str) + "-" + log[att].astype(int).astype(str)
        log["MIN"] = log["minutes"].round(0).astype(int) if "minutes" in log else None
        cols = [c for c in ["Date", "Game", "Result", "MIN", "pts", "reb", "ast", "stl", "blk", "tov", "FG", "3P", "FT", "plus_minus"]
                if c in log]
        config = {c: st.column_config.NumberColumn(stats.label(c) if c != "plus_minus" else "+/-", format="%d")
                  for c in ["pts", "reb", "ast", "stl", "blk", "tov", "plus_minus"] if c in cols}
        st.dataframe(log[cols], hide_index=True, width="stretch", column_config=config, height=420)