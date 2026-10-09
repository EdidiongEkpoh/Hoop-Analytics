'''Explorer: plot any two stats, filter the pool, and find who stands out, in one season or across the decade.'''
import streamlit as st 
from lib import charts, components as ui, filters, nav, queries, stats 

f = filters.current()
if f is None:
    ui.empty_state("No data yet.")

ui.page_header("Explorer", "Pick any two stats to find who stands out. Click a point or a row to open that player's profile.")
G = f.grain 
data = queries.player_seasons(f.season_type)
if data.empty:
    ui.empty_state(f"No {f.season_type.lower()} data.")
    st.stop() 

AXES = [stats.column(k, G) for k in ["pts", "reb", "ast", "stl", "blk", "tov"]] + [
    "ts_pct", "relative_ts_pct", "efg_pct", "fg3_pct", "ft_pct", "fg3pr", "ftr", "usage", "assist_pct",
    "tov_pct", "oreb_pct", "dreb_pct", "reb_pct", "stl_pct", "blk_pct", "offensive_rating", "defensive_rating",
    "net_rating", "minutes_per_game", "games_played"
]

c1, c2, c3, c4 = st.columns([1.3, 1.3, 1.6, 1.6])
scope = c1.segmented_control("Seasons", ["This Season", "All Seasons"], default="This Season", key="ex_scope") or "This Season"
x = c2.selectbox("Horziontal Axis", AXES, index=AXES.index("usage"), format_func=stats.label, key="ex_x")
y = c3.selectbox("Vertical Axis", AXES, index=AXES.index("ts_pct"), format_func=stats.label, key="ex_y")
groups = c4.multiselect("Positions", ["Guard", "Forward", "Center"], default=["Guard", "Forward", "Center"], key="ex_pos")

c1, c2, c3 = st.columns([1.3, 2.9, 1.6])
qualified = c1.toggle("Qualified Players Only", value=True, key="ex_qualified",
                      help="Players who meet the games and minutes thresholds for that season.")
min_mpg = c2.slider("Minimum Minutes Per Game", 0, 36, 0, key="ex_mpg")
team_names = sorted(data["last_team_name"].dropna().unique())
team = c3.selectbox("Team", ["All Teams"] + team_names, key="ex_team")

df = data if scope == "All Seasons" else data[data["season"] == f.season]
df = df[df["position_group"].isin(groups) & (df["minutes_per_game"] >= min_mpg)]
if qualified:
    df = df[df["is_eligible"]]
if team != "All Teams":
    df = df[df["last_team_name"] == team]
df = df.dropna(subset=[x, y]).copy()
df["label"] = df["last_team_name"].fillna("") + ", " + df["season"]

names = sorted(df["player_name"].unique())
highlight_names = st.multiselect("Highlight Players", names, key="ex_highlight", placeholder="Type a name")
highlight = set(df.loc[df['player_name'].isin(highlight_names), "player_id"])

if df.empty:
    ui.empty_state("No players match these filters.", "Loosen the minutes, position, or team filters.")
    st.stop()

where = f"every {f.season_type.lower()} in the data" if scope == "All Seasons" else f"{f.season} {f.season_type.lower()}"
st.caption(f"{len(df)} player-seasons from {where}. Dotted lines are the medians. "
           f"Counting stats are {stats.GRAIN_LABELS[G].lower()}. Drag to zoom; double-click to reset.")
event = st.plotly_chart(charts.explorer_scatter(df, x, y, highlight=highlight), theme=None, width="stretch",
                        key="ex_scatter", on_select="rerun", selection_mode="points")
points = event.selection.points if event and event.selection else []
if points and points[0].get("customdata"):
    player_id, season = points[0]["customdata"][0], points[0]["customdata"][1]
    nav.open_player(player_id, season=season)

st.subheader("Leaderboard")
st.caption(f"Sorted by {stats.label(y)}; click a column header to sort by it, or a row to open the player profile.")
board = df.sort_values(y, ascending=stats.get(y).better is False).reset_index(drop=True)
keys = ["player_name", "last_team_name"] + (["season"] if scope == "All Season" else []) + \
       ["games_played", "minutes_per_game"] + list(dict.fromkeys([x, y, stats.column("pts", G), "ts_pct", "usage"]))
picked = ui.data_table(board, keys, labels={"player_name": "Player", "last_team_name": "Team", "season": "Season"},
                        selectable=True, key="ex_board", height=480)

if picked is not None:
    nav.open_player(board.loc[picked, "player_id"], season=board.loc[picked, "season"])