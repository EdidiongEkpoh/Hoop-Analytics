import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
def inject_css():
    st.markdown(
        '''
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter: wght@400;500;600;700&display=swap');

        html, body, [class*="css"] { font-family: 'Inter', sans-serif; font-size: 16px }

        [data-testid="stMetric"] {
            background-color: #1A1D24;
            border: 1px solid #2A2E37;
            border-radius: 12px;
            padding: 14px 18px;
        }
        [data-testid="stMetricLabel"] { font-size: 13px; color: #9A9EA6; }
        [data-testid="stMetricValue"] { font-size: 26px; font-weight: 600; }

        [data-testid="stCaptionContainer"] { font-size: 15px !important; }

        h1 { font-size: 38px !important; font-weight: 700; }
        h2 { font-size: 26px !important; font-weight: 600; }
        h3 { font-size: 20px !important; font-weight: 600; }
        </style>
        ''',
        unsafe_allow_html=True
    )

def rank_badge_html(rank, n):
    rank = int(rank)
    n = int(n)
    goodness = (n - rank) / (n - 1) if n > 1 else 1.0
    hue = goodness * 120 
    color = f"hsl({hue:.0f}, 65%, 42%)"
    return (
        f'<span style="background: {color}; color:white; padding:2px 10px; '
        f'border-radius:12px; font-size:12px; font-weight:600; '
        f'display:inline-block; margin-top:4px;">#{rank} of {n}</span>'
    )

def conference_badge(name, color):
    return (
        f'<span style="background:{color}; color: white; padding:4px 14px; '
        f'border-radius:8px; font-size:14px; font-weight:700; letter-spacing:0.5px; '
        f'display:inline-block;">{name.upper()}</span>'
    )

def _ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n%10, "th")
    return f"{n}{suffix}"

def percentile_badge_html(percentile, higher_is_better):
    pct = float(percentile)
    label = _ordinal(int(round(pct*100)))

    if higher_is_better is None:
        color = "hsl(220, 10%, 45%)" # neutral gray
    else:
        goodness = pct if higher_is_better else (1 - pct)
        hue = goodness * 120
        color = f"hsl({hue:.0f}, 65%, 42%)"
    return (
        f'<span style="background:{color}; color:white; padding:2px 10px; '
        f'border-radius:12px; font-size: 12px; font-weight:600; '
        f'display:inline-block; margin-top:4px;">{label} percentile</span>'
    )


def render_percentile_bars(rows):
    html_parts = []
    for label, pct, higher_is_better in rows:
        if pct is None:
            continue 
        pct = float(pct)
        hue = pct * 120 if higher_is_better else (1-pct) * 120
        color = f"hsl({hue:.0f}, 60%, 50%)"
        html_parts.append(f"""
        <div style="margin-bottom:10px;">
            <div style="display:flex; justify-content: space-between; font-size: 13px; color #9A9EA6; margin-bottom: 4px;">
            <span>{label}</span><span style="color:#E8E8E8; font-weight: 600;">{pct*100:.0f}th</span>
        </div>
        <div style="background:#2A2E37; border-radius: 6px; height:8px; overflow:hidden;">
            <div style="width:{pct*100:.0f}; background:{color}; height:100%; border-radius:6px;"></div>
            </div>
        </div>
        """
        )
    return "".join(html_parts)


def arc_points(cx, cy, r, theta1, theta2, n=50):
    thetas = np.linspace(np.radians(theta1), np.radians(theta2), n)
    return cx + r * np.cos(thetas), cy + r * np.sin(thetas)

def draw_court(fig, line_color="#4A4E58"):
    
    def add_line(x, y, dash=None):
        fig.add_trace(go.Scatter(
            x=x, y=y, mode="lines", line=dict(color=line_color, width=1.5, dash=dash),
            showlegend=False, hoverinfo="skip"
        ))
    
    # Hoop 
    hx, hy = arc_points(0, 0, 7.5, 0, 360)
    add_line(hx, hy)

    # Backboard
    add_line([-30, 30], [-7.5, -7.5])

    # Paint
    add_line([-80, -80, 80, 80], [-47.5, 142.5, 142.5, -47.5])
    add_line([-60, -60, 60, 60], [-47.5, 142.5, 142.5, -47.5])

    # Free Throw Circle
    ftx, fty = arc_points(0, 142.5, 60, 0, 180)
    add_line(ftx, fty)
    ftx2, fty2 = arc_points(0, 142.5, 60, 180, 360)
    add_line(ftx2, fty2, dash="dash")

    # Restricted Area
    rax, ray = arc_points(0, 0, 40, 0, 180)
    add_line(rax, ray)

    # Corner Three Sidelines and Three Point Arc
    add_line([-220, -220], [-47.5, 92.5])
    add_line([220, 220], [-47.5, 92.5])
    tpx, tpy = arc_points(0, 0, 237.5, 22, 158)
    add_line(tpx, tpy)
    
    # Halfcourt Circles
    hcx, hcy = arc_points(0, 422.5, 60, 180, 360)
    add_line(hcx, hcy)
    hcx2, hcy2 = arc_points(0, 422.5, 20, 180, 360)
    add_line(hcx2, hcy2)

    # Court Outline
    add_line([-250, -250, 250, 250, -250], [-47.5, 422.5, 422.5, -47.5, -47.5])


def comparison_row_html(label, left_val, right_val, left_display, right_display, higher_is_better=True):
    if left_val is None or right_val is None or pd.isna(left_val) or pd.isna(right_val) or left_val == right_val:
        left_color = right_color = "#E8E8E8"
    elif (left_val > right_val) == higher_is_better:
        left_color, right_color = "#5DCAA5", "#9A9EA6"
    else:
        left_color, right_color = "#9A9EA6", "#5DCAA5"

    return f"""
    <div style="display:flex; align-items:center; padding:10px 0; border-bottom:1px solid #2A2E37;">
        <div style="flex:3; text-align:right; font-size:20px; font-weight:700; color:{left_color}; padding-right:24px;">{left_display}</div>
        <div style="flex:1; text-align:center; font-size:13px; color:#9A9EA6;">{label}</div>
        <div style="flex:3; text-align:left; font-size:20px; font-weight:700; color:{right_color}; padding-left:24px;">{right_display}</div>
    </div>
    """