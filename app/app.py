import streamlit as st 
from lib import charts
from lib import filters 
from lib.components import inject_css 

st.set_page_config(page_title="Hoop Analytics", layout="wide")
inject_css()
filters.keep_alive()

pages = [
    st.Page("views/league.py", title="League", default=True),
    st.Page("views/teams.py", title="Teams", url_path="teams"),
    st.Page("views/players.py", title="Players", url_path="players"),
    st.Page("views/compare.py", title="Compare", url_path="compare"),
    st.Page("views/explorer.py", title="Explore", url_path="explorer"),
    st.Page("views/about.py", title="About", url_path="about")
]
page = st.navigation(pages, position="top")

FILTERS = {
    "": dict(show_grain=False), # League
    "teams": dict(show_grain=True),
    "players": dict(show_grain=True),
    "compare": dict(show_grain=True),
    "explorer": dict(show_grain=True),
    "about": None
}
config = FILTERS.get(page.url_path, {})
if config is not None:
    filters.render(**config)

page.run()