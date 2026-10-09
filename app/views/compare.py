'''Compare two players or two teams from any season'''
from html import escape 
import pandas as pd
import streamlit as st 
from lib import charts, components as ui, filters, queries, stats 
from lib.percentiles import add_percentiles 

f = filters.current()
if f is None:
    ui.empty_state("No data yet.")
    st.stop()

ui.page_header("Compare", "Two players or two teams, side by side comparisons for any available season")
mode = st.segmented_control("Compare", ["Players", "Teams"], default="Players", key="cmp_mode", label_visibility="collapsed") or "Players"

G = f.grain

def side_header(title, sub, image, accent):
    return (f'<div style="text-align:center"><img src="{escape(image)}" alt="" style="height:120px">'
            f'<div style="font-family:{charts.DISPLAY_FONT};font-size:1.9rem;font-weight:600;color:{accent}">{escape(title)}</div>'
            f'<div style="color:{charts.MUTED}">{escape(sub)}</div></div>')

def compare_rows(groups, left, right):
    for title, keys in groups:
        st.subheader(title)
        st.markdown("".join(ui.comparison_row(k, left.get(k), right.get(k)) for k in keys), unsafe_allow_html=True)
        st.write("")

if mode == "Players":
    data = queries.player_seasons(f.season_type)
    if data.empty:
        ui.empty_state(f"No {f.season_type.lower()} data.")
        st.stop()
    pct_keys = ["pts", "reb", "ast", "stl", "blk", "ts_pct", "relative_ts_pct", "fg3_pct", "fg3pr", "ftr", "usage", "assist_pct",
                "tov_pct", "reb_pct", "stl_pct", "blk_pct"]
    pct_cols = [stats.column(k, G) for k in pct_keys]

    def pick(col, side, default_rank):
        with col:
            season = st.selectbox("Season", f.seasons, index=f.seasons.index(f.season), key=f"cmp_{side}_season")
            s = data[data["season"] == season].sort_values("total_minutes", ascending=False)
            if s.empty:
                ui.empty_state(f"No {f.season_type.lower()} data {season}.")
                return None 
            ids = s["player_id"].tolist()
            names = dict(zip(ids, s['player_name'] + ", " + s["last_team_name"].fillna("")))
            remembered = st.session_state.get("player_id") if side == "a" else None 
            default = remembered if remembered in names else ids[min(default_rank, len(ids) - 1)]
            options = sorted(ids, key=lambda i: names[i])
            player_id = st.selectbox("Player", options, index=options.index(default), format_func=names.get, key=f"cmp_{side}_player")
            ranked = add_percentiles(s, pct_cols)
            return ranked.set_index("player_id").loc[player_id], season 

    left, right = st.columns(2)
    a = pick(left, "a", 0)
    b = pick(right, "b", 1)
    if a is None or b is None:
        st.stop()
    (pa, sa), (pb, sb) = a, b

    hl, hr = st.columns(2)
    hl.markdown(side_header(pa["player_name"], f"{sa}, {pa['last_team_name']}", charts.headshot_url(pa.name), charts.MAPLE),
                unsafe_allow_html=True)
    hr.markdown(side_header(pb["player_name"], f"{sb}, {pb['last_team_name']}", charts.headshot_url(pb.name), charts.ACCENT_2),
                    unsafe_allow_html=True)
    st.subheader("Profiles")
    st.caption("Each player's percentile among qualified players in their own season. "
                f"Counting stats are {stats.GRAIN_LABELS[G].lower()}.")
    for p, s in ((pa, sa), (pb, sb)):
        if not p["is_eligible"]:
            st.caption(f"{p['player_name']} in {s} is below the qualifying threshold; his percentiles compare them with qualified players.")
    c1, c2 = st.columns(2)
    with c1:
        compare_rows([("Production", ["games_played", "minutes_per_game"] + [stats.column(k, G) for k in ["pts", "reb", "ast", "stl", "blk", "tov"]])], pa, pb)
    with c2:
        compare_rows([("Shooting", ["ts_pct", "relative_ts_pct", "efg_pct", "fg2_pct", "fg3_pct", "ft_pct", "fg3pr", "ftr"])], pa, pb)
    c1, c2 = st.columns(2)
    with c1:
        compare_rows([("Role and Playmaking", ["usage", "assist_pct", "tov_pct", "oreb_pct", "dreb_pct", "reb_pct"])], pa, pb)
    with c2:
        compare_rows([("Defense and Impact", ["stl_pct", "blk_pct", "offensive_rating", "defensive_rating", "net_rating"])], pa, pb)
    
    label_a = pa["player_name"] + ("" if sa == sb else f" ({sa})")
    label_b = pb["player_name"] + ("" if sa == sb else f" ({sb})")
    rows = [(stats.label(k), pa.get(f"{c}_pctile"), pb.get(f"{c}_pctile")) for k, c in zip(pct_keys, pct_cols)]
    charts.show(charts.percentile_compare(rows, label_a, label_b), key="cmp_pct")

    

else:
    data = queries.team_seasons(f.season_type)
    if data.empty:
        ui.empty_state(f"No {f.season_type.lower()} data.")
        st.stop()
    pct_keys = ["offensive_rating", "defensive_rating", "net_rating", "efg_pct", "tov_pct", "oreb_pct", "ftr", "opp_efg_pct",
                "opp_tov_pct", "dreb_pct", "opp_ftr", "fg3pr", "ts_pct", "ast_to_tov"]

    def pick(col, side, default_rank):
        with col:
            season = st.selectbox("Season", f.season, index=f.seasons.index(f.season), key=f"cmpt_{side}_season")
            s = data[data["season"] == season].sort_values("win_pct", ascending=False)
            if s.empty:
                ui.empty_state(f"No {f.season_type.lower()} data for {season}.")
                return None 
            ids = s["team_id"].astype(str).tolist()
            names = dict(zip(ids, s["team_name"]))
            remembered = st.session_state.get("team_id") if side == "a" else None 
            default = remembered if remembered in names else ids[min(default_rank, len(ids) - 1)]
            options = sorted(ids, key=lambda i: names[i])
            team_id = st.selectbox("Team", options, index=options.index(default), format_func=names.get, key=f"cmpt_{side}_team")
            ranked = add_percentiles(s.assign(team_id=s["team_id"].astype(str)), pct_keys, pool_mask=pd.Series(True, index=s.index))
            return ranked.set_index("team_id").loc[team_id], season

    left, right = st.columns(2)
    a = pick(left, "a", 0)
    b = pick(right, "b", 1)
    if a is None or b is None:
        st.stop()
    (ta, sa), (tb, sb) = a, b
    hl, hr = st.columns(2)
    hl.markdown(side_header(ta["team_name"], f"{sa}, {int(ta['wins'])}-{int(ta['losses'])}", charts.team_logo_url(ta.name), charts.MAPLE),
                unsafe_allow_html=True)
    hr.markdown(side_header(tb["team_name"], f"{sb}, {int(tb['wins'])}-{int(tb['losses'])}", charts.team_logo_url(tb.name), charts.ACCENT_2),
                    unsafe_allow_html=True)

    st.subheader("Profiles")
    c1, c2 = st.columns(2)
    with c1:
        compare_rows([("Ratings", ["win_pct", "offensive_rating", "defensive_rating", "net_rating", "pace"]),
                        ("Four Factors, Offense", ["efg_pct", "tov_pct", "oreb_pct", "ftr"])], ta, tb)
    with c2:
        compare_rows([("Shooting", ["ts_pct", "fg3_pct", "fg3pr", "ft_pct", "ast_to_tov"]),
                                ("Four Factors, Defense", ["opp_efg_pct", "opp_tov_pct", "dreb_pct", "opp_ftr"])], ta, tb)
    st.caption("Each team's percentile among all teams in its own season")
    if data[data["season"] == sa].shape[0] < 10:
        st.caption("Fewer than 10 teams in this season's pool, so percentiles are not shown")
    label_a = ta["team_name"] + ("" if sa == sb else f" ({sa})") 
    label_b = tb["team_name"] + ("" if sa == sb else f" ({sb})") 
    rows = [(stats.label(k), ta.get(f"{k}_pctile"), tb.get(f"{k}_pctile")) for k in pct_keys]
    charts.show(charts.percentile_compare(rows, label_a, label_b), key="cmpt_pct")
    