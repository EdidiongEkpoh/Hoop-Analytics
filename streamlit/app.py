import streamlit as st

st.set_page_config(page_title="Hoop Analytics", layout="wide")

league_overview = st.Page('home.py', title="League Overview", default=True)
team_profile = st.Page("team_profile.py", title="Team Profile")
player_profile = st.Page("player_profile.py", title="Player Profile")
comparison = st.Page("comparison.py", title="Comparison")

pg = st.navigation([league_overview, team_profile, player_profile, comparison], position="top")
pg.run()