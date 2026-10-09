'''
'''
import pandas as pd
import streamlit as st
from lib import filters 

PLAYER_PAGE = "views/players.py"
TEAM_PAGE = "views/teams.py"

def open_player(player_id, season=None):
    st.session_state['player_id'] = str(player_id)
    if season:
        filters.request_season(season)
    st.switch_page(PLAYER_PAGE)

def open_team(team_id, season=None):
    st.session_state['team_id'] = str(team_id)
    if season:
        filters.request_season(season)
    st.switch_page(TEAM_PAGE)

def _chosen(kind):
    '''The player or team to show. Retrieves the session state first, then the URL.'''
    return st.session_state.get(f"{kind}_id") or st.query_params.get(kind)

def _store(kind, widget_key):
    st.session_state[f"{kind}_id"] = st.session_state[widget_key]
def player_picker(season_df, container=None):
    '''A searchable player selector for one season.'''
    container = container or st 
    df = season_df.sort_values("total_minutes", ascending=False)
    ids = df['player_id'].astype(str).tolist()
    names = dict(zip(ids, df['player_name'] + ", " + df['last_team_name'].fillna("")))
    wanted, note = _chosen('player'), None 
    if wanted not in names:
        if wanted:
            note = wanted 
        wanted = ids[0]
    options = sorted(ids, key=lambda i: names[i])
    choice = container.selectbox("Player", options, index=options.index(wanted), format_func=names.get,
                                key="pick_player", on_change=_store, args=('player', 'pick_player'))
    st.session_state['player_id'] = choice 
    st.query_params['player'] = choice 
    return df.set_index(df['player_id'].astype(str)).loc[choice], note 

def team_picker(team_df, container=None):
    '''A team selector for one season; defaults to the team with the best record.'''
    container = container or st 
    df = team_df.sort_values('win_pct', ascending=False)
    ids = df['team_id'].astype(str).tolist()
    names = dict(zip(ids, df['team_name']))
    wanted = _chosen('team')
    if wanted not in names:
        wanted = ids[0]
    options = sorted(ids, key=lambda i: names[i])
    choice = container.selectbox("Team", options, index=options.index(wanted), format_func=names.get,
                                 key="pick_team", on_change=_store, args=('team', 'pick_team'))
    st.session_state['team_id'] = choice 
    st.query_params['team'] = choice 
    return df.set_index(df['team_id'].astype(str)).loc[choice]
