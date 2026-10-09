'''
The filter bar for every page: season, season type, stat grain
'''
from dataclasses import dataclass
import streamlit as st
from lib import queries
from lib.stats import GRAINS, GRAIN_LABELS 

params = {"season": "season", "season_type": "type", "grain": "grain"}

@dataclass(frozen=True)
class Filters:
    season: str 
    season_type: str 
    grain: str 
    seasons: list[str]

    @property 
    def previous_season(self):
        i = self.seasons.index(self.season)
        return self.seasons[i + 1] if i + 1 < len(self.seasons) else None 

    @property 
    def is_current(self):
        return self.season == self.seasons[0]

def _seed(key, valid, default):
    '''Before a widget is drawn take the URL value on the first load and replace anything invalid.'''
    if key not in st.session_state:
        from_url = st.query_params.get(params[key])
        st.session_state[key] = from_url if from_url in valid else default 
    elif st.session_state[key] not in valid:
        st.session_state[key] = default 

def keep_alive():
    '''
    Streamlit deletes a widget's state after any run that doesn't draw it (the About page or League page for grain).
    Re-assigning the keys at the start of each run keeps the selections. Called by app.py before navigation.
    '''
    for key in params:
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]

def render(show_season_type=True, show_grain=True):
    '''Draw the filter row. Called by app.py before the page runs.'''
    seasons = queries.seasons()
    if not seasons:
        return 
    _seed("season", seasons, seasons[0])
    # Clicking the active grain deselects it and restores the last grain chosen.
    if "grain" in st.session_state and st.session_state['grain'] is None:
        st.session_state['grain'] = st.session_state.get('_last_grain', 'per_game')
    _seed('grain', list(GRAINS.values()), 'per_game')
    st.session_state['_last_grain'] = st.session_state['grain']

    cols = st.columns([1.2, 1.2, 2.4, 3])
    cols[0].selectbox("Season", seasons, key="season")
    # Season types depend on the season chosen: a new season has no playoffs yet
    types = queries.season_types(st.session_state['season']) or ['Regular Season']
    _seed("season_type", types, "Regular Season" if "Regular Season" in types else types[0])
    if show_season_type:
        cols[1].selectbox("Season type", types, key="season_type")
    if show_grain:
        cols[2].segmented_control("Stats", list(GRAINS.values()), format_func=GRAIN_LABELS.get, key="grain")

    st.query_params.update({params[k]: st.session_state[k] for k in params})

def current():
    '''The current selections for pages. None when the database has no seasons yet.'''
    seasons = queries.seasons() 
    if not seasons or "season" not in st.session_state:
        return None
    return Filters(
        season=st.session_state['season'],
        season_type=st.session_state.get('season_type', 'Regular Season'),
        grain=st.session_state.get('grain') or st.session_state.get('_last_grain', 'per_game'),
        seasons=seasons
    )

