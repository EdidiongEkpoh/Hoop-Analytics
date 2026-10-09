'''
UI script that builds HTML foundation
'''
from html import escape 
import pandas as pd
import streamlit as st
from lib import charts, stats
from lib.percentiles import goodness 

C = charts 

def inject_css():
    st.markdown(
        f'''
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&&display=swap');

        html, body [class*="css"], .stMarkdown, .stDataFrame, button, input, select {{
            font-family: {C.BODY_FONT};
        }}
        h1, h2, h3, h4 {{
            font-family: {C.DISPLAY_FONT} !important;
            font-weight: 600 !important;
            letter-spacing: 0.2px;
        }}
        h1 {{ font-size: 2.6rem !important; line-height: 1.05 !important; }}
        h2 {{ font-size: 1.75rem !important; }}
        h3 {{ font-size: 1.3rem !important; }}
        
        [data-testid="stMainBlockContainer"] {{ padding-top: 2.2rem; }}
        .hc-header {{ display: flex; align-items: center; gap: 20px; margin: 0.25rem 0 1.25rem; }}
        .hc-header img {{ height: 96px; width: auto; }}
        .hc-header h1 {{ margin: 0; padding: 0; }}
        .hc-header .hc-sub {{ color: {C.MUTED}; font-size: 1rem; margin-top: 4px; }}

        .hc-stat {{ background: {C.PANEL}; border-radius: 6px; padding: 12px 16px 14px; height: 100%; }}
        .hc-stat-label {{ color: {C.MUTED}; font-size: 0.85rem; }}
        .hc-stat-value {{
            font-family: {C.DISPLAY_FONT}; font-size: 2.3rem; font-weight: 600; line-height 1.1;
            font-variant-numeric: tabular-nums; color: {C.TEXT};
        }}
        .hc-stat-delta, .hc-stat-note {{ font-size: 0.85rem; font-variant-numeric: tabular-nums; }}
        .hc-stat-note {{ color: {C.MUTED}; }}

        .hc-pbar {{ margin-bottom: 11px; }}
        .hc-pbar-top {{ display: flex; justify-content: space-between; font-szie: 0.9rem; margin-bottom: 4px; }}
        .hc-pbar-label {{ color: {C.MUTED}; }}
        .hc-pbar-value {{ font-variant-numeric: tabular-nums; color: {C.TEXT}; }}
        .hc-pbar-track {{ display: flex; align-items: center; gap: 10px; }}
        .hc-pbar-rail {{ flex: 1; background: {C.LINE}; border-radius: 3px; height: 8px; overflow: hidden; }}
        .hc-pbar-fill {{ height: 100%; border-radius: 3px; }}
        .hc-pbar-pct {{ width: 2.2rem; text-align: right; font-family: {C.DISPLAY_FONT}; font-size: 1.05rem;
                        font-variant-numeric: tabular-nums; color: {C.TEXT}; }}

        .hc-cmp {{ display: grid; grid-template-columns: 1fr minmax(120px, auto) 1fr; align-items: center;
                    padding: 8px 0; border-bottom: 1px solid {C.LINE}; }}
        .hc-cmp-val {{ font-family: {C.DISPLAY_FONT}; font-szie: 1.45rem; font-variant-numeric: tabular-nums; }}
        .hc-cmp-left {{ text-align: right; padding-right: 20px; }}
        .hc-cmp-right {{ text-align: left; padding-left: 20px; }}
        .hc-cmp-label {{ text-align: center; color: {C.MUTED}; font-size: 0.9rem; }}

        .hc-empty {{ border: 1px dashed {C.LINE}; border-radius: 6px; padding: 18px 20px; color: {C.MUTED}; }}
        .hc-empty strong {{ color: {C.TEXT}; font-weight: 500; }}
        </style>
        '''
        , unsafe_allow_html=True
    )

def page_header(title, subtitle=None, image_url=None):
    img = f'<img src="{escape(image_url)}" alt="">' if image_url else ""
    sub = f'<div class="hc-sub">{escape(subtitle)}</div>' if subtitle else ""
    st.markdown(f'<div class="hc-header">{img}<div><h1>{escape(title)}</h1>{sub}</div></div>', unsafe_allow_html=True)

def stat_card(label, value, delta=None, delta_good=None, note=None):
    '''HTML for for one stat card'''
    color = C.MUTED if delta_good is None else (C.BETTER if delta_good else C.WORSE)
    delta_html = f'<div class="hc-stat-delta" style="color:{color}">{escape(delta)}</div>' if delta else ""
    note_html = f'<div class="hc-stat-note">{escape(note)}</div>' if note else ""
    return (f'<div class="hc-stat"><div class="hc-stat-label">{escape(label)}</div>'
            f'<div class="hc-stat-value">{escape(value)}</div>{delta_html}{note_html}</div>')

def stat_cards(cards):
    for col, card in zip(st.columns(len(cards)), cards):
        col.markdown(card, unsafe_allow_html=True)

def season_delta(key, current, previous=None, previous_season=None):
    if previous is None or pd.isna(previous) or current is None or pd.isna(current):
        return None, None 
    stat = stats.get(key)
    diff = current - previous 
    text = f"{stats.fmt(diff, format_code=stats.DIFF_FMT.get(stat.fmt, stat.fmt))} vs {previous_season}"
    good = None if stat.better is None or diff == 0 else ((diff > 0) == stat.better)
    return text, good

def percentile_bars(rows):
    '''
    rows: (stat key, value, percentile 0-1). Bars fill to the percentile and are colored by goodness.
    '''
    parts = []
    for key, value, pctile in rows:
        stat = stats.get(key)
        if pctile is None or pd.isna(pctile):
            fill, pct_text, width = C.NEUTRAL, "-", 0
        else:
            fill = C.goodness_color(goodness(pctile, stat.better))
            pct_text, width = f"{round(pctile * 100):d}", round(pctile * 100)
        parts.append(
            f'<div class="hc-pbar" title="{escape(stat.desc)}">'
            f'<div class="hc-pbar-top"><span class="hc-pbar-label">{escape(stat.label)}</span>'
            f'<span class="hc-pbar-value">{escape(stats.fmt(value, key))}</span></div>'
            f'<div class="hc-pbar-track"><div class="hc-pbar-rail">'
            f'<div class="hc-pbar-fill" style="width:{width}%; background:{fill}"</div></div>'
            f'<span class="hc-pbar-pct">{pct_text}</span></div></div>'
        )
    st.markdown("".join(parts), unsafe_allow_html=True)

def comparison_row(key, left, right):
    '''HTML for one side-by-side row in the comparison page'''
    stat = stats.get(key)
    lc = rc = C.TEXT
    if stat.better is not None and not (pd.isna(left) or pd.isna(right)) and left != right:
        left_wins = (left > right) == stat.better 
        lc, rc = (C.BETTER, C.MUTED) if left_wins else (C.MUTED, C.BETTER)
    return (f'<div class="hc-cmp"><div class="hc-cmp-val hc-cmp-left" style="color:{lc}">{escape(stats.fmt(left, key))}</div>'
            f'<div class="hc-cmp-label" title="{escape(stat.desc)}">{escape(stat.label)}</div>'
            f'<div class="hc-cmp-val hc-cmp-right" style="color:{rc}">{escape(stats.fmt(right, key))}</div></div>')

def empty_state(message, hint=None):
    hint_html = f"<br>{escape(hint)}" if hint else ""
    st.markdown(f'<div class="hc-empty"><strong>{escape(message)}</strong>{hint_html}</div>', unsafe_allow_html=True)


def data_table(df, keys, labels=None, selectable=False, key=None, height=None, pinned=None):
    display, config = stats.table_config(df, keys, labels, pinned)
    kwargs = dict(column_config=config, hide_index=True, key=key)
    if height:
        kwargs['height'] = height 
    if selectable:
        kwargs.update(on_select="rerun", selection_mode="single-row")
    try:
        event = st.dataframe(display, width="stretch", **kwargs)
    except TypeError: # older Streamlit version without "stretch"
        event = st.dataframe(display, use_container_width=True, **kwargs)
    if selectable and event is not None:
        rows = event.selection.rows
        return display.index[rows[0]] if rows else None 
    return None
