import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st 
from plotly.subplots import make_subplots 
from lib import stats 
import base64
import requests
import logging

NAVY = "#0E1726"
PANEL = "#172235"
LINE = "#26344D"
TEXT = "#E7E8F3"
MUTED = "#8F9AB0"
MAPLE = "#E2A65A"
BETTER = "#008000"
WORSE = "#E4675E"
NEUTRAL = "#5B667A"

DISPLAY_FONT = "'Plus Jakarta Sans', 'Helvetica Neue', 'Arial', sans-serif"
BODY_FONT = "'Plus Jakarta Sans', 'Helvetica Neue', 'Arial', sans-serif"

ACCENT_2 = "#9BB0D0"
ZONE_ORDER = ["Restricted Area", "In The Paint (Non-RA)", "Mid-Range", "Left Corner 3", "Right Corner 3", "Above the Break 3"]
ZONE_LABELS = {"Restricted Area": "At the rim", "In The Paint (Non-RA)": "Paint (non-rim)", "Mid-Range": "Mid-range",
               "Left Corner 3": "Left corner 3", "Right Corner 3": "Right corner 3", "Above the Break 3": "Above the break 3"}

def _hex_to_rgb(h):
    return np.array([int(h[i:i+2], 16) for i in (1, 3, 5)], dtype=float)

def goodness_color(g=None):
    if g is None or pd.isna(g):
        return NEUTRAL
    g = min(max(float(g), 0.0), 1.0)
    lo, mid, hi = _hex_to_rgb(WORSE), _hex_to_rgb(NEUTRAL), _hex_to_rgb(BETTER)
    rgb = lo + (mid - lo) * (g / 0.5) if g < 0.5 else mid + (hi - mid) * ((g - 0.5) / 0.5)
    return "#" + "".join(f"{int(round(c)):02x}" for c in rgb)


pio.templates["hoop"] = go.layout.Template(
    layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=BODY_FONT, color=TEXT, size=13),
        title=dict(font=dict(family=DISPLAY_FONT, size=20, color=TEXT), x=0, xanchor="left"),
        colorway=[MAPLE, BETTER, "#9BB0D0", WORSE, "#7FC8A9", "#C9A0DC"],
        xaxis=dict(gridcolor=LINE, linecolor=LINE, zerolinecolor=LINE, tickfont=dict(color=MUTED)),
        yaxis = dict(gridcolor=LINE, linecolor=LINE, zerolinecolor=LINE, tickfont=dict(color=MUTED)),
        hoverlabel=dict(bgcolor=PANEL, bordercolor=LINE, font=dict(family=BODY_FONT, color=TEXT)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED)),
        margin=dict(l=8, r=8, t=36, b=8)

    )
)
pio.templates.default = "plotly_dark+hoop"

def show(fig, key=None):
    try:
        st.plotly_chart(fig, theme=None, width="stretch", key=key)
    except TypeError: # for older streamlit versions without width="stretch"
        st.plotly_chart(fig, theme=None, use_container_width=True, key=key)

def headshot_url(player_id):
    return f"https://cdn.nba.com/headshots/nba/latest/260x190/{player_id}.png"

LOGO_URLS = (
    "https://cdn.nba.com/logos/nba/{team_id}/global/L/logo.svg",
    "https://cdn.nba.com/logos/nba/{team_id}/primary/L/logo.svg"
)

_IMAGE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windos NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0 Safari/537.36",
    "Referer": "https://www.nba.com/",
    "Accept": "image/svg+xml,image/*;q=0.9,*/*;q=0.5"
}
log = logging.getLogger(__name__)

@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)
def _image_data_uri(urls):
    for url in urls:
        try:
            r = requests.get(url, headers=_IMAGE_HEADERS, timeout=5)
        except requests.RequestException as e:
            log.warning("Image request failed fro %s: %s", url, e)
            continue 
        ctype = r.headers.get("content-type", "").split(';')[0].strip().lower()
        body = r.content 
        looks_svg = body.lstrip()[:5] in (b"<svg ", b"<svg>", b"<?xml")
        if r.ok and body and (ctype.startswith("image/") or looks_svg):
            if not ctype.startswith("image/"):
                ctype="image/svg+xml"
            return f"data:{ctype};base64,{base64.b64encode(body).decode()}"
        log.warning("Image not usable from %s: HTTP %s, content-type %r", url, r.status_code, ctype)
    raise LookupError(f"No image at {urls}")

def team_logo_url(team_id):
    try: 
        return _image_data_uri(tuple(u.format(team_id=team_id) for u in LOGO_URLS)) 
    except LookupError:
        return None
def trend_chart(df, y, all_seasons, highlight=None, league=None, height=260):
    order = sorted(all_seasons)
    data = df.set_index("season").reindex(order)
    stat = stats.get(y)
    text = [stats.fmt(v, y) for v in data[y]]
    eligible = data['is_eligible'].fillna(False).astype(bool) if "is_eligible" in data else pd.Series(True, index=data.index)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
            x=order, y=data[y], mode="lines+markers", name=stat.label, connectgaps=False,
            line=dict(color=TEXT, width=2),
            marker=dict(size=[12 if s == highlight else 8 for s in order],
                        color=[MAPLE if s == highlight else (TEXT if e else NAVY) for s, e in zip(order, eligible)],
                        line=dict(color=[MAPLE if s == highlight else TEXT for s in order], width=2),
                        ),
                        text=text, customdata=np.where(eligible, "", " (small sample)"),
                        hovertemplate="%{x}: %{text}%{customdata}<extra></extra>"
        ))
    tickformat = ".1%" if stat.fmt == "pct" else None 
    fig.update_layout(
        height=height, showlegend=league is not None, title=stat.label,
        yaxis=dict(tickformat=tickformat), xaxis=dict(type="category"),
        legend=dict(orientation="h", y=1.12, x=1, xanchor="right")
    )
    return fig


def on_off_chart(row, metrics, height_per_metric=52):
    n = len(metrics)
    fig = make_subplots(rows=n, cols=1, vertical_spacing=0.25/max(n, 1))
    for i, m in enumerate(metrics, start=1):
        on, off = row.get(f"on_{m}"), row.get(f"off_{m}")
        stat = stats.get(m)
        if pd.isna(on) or pd.isna(off):
            continue
        improved = None if stat.better is None else ((on > off) == stat.better)
        color = NEUTRAL if improved is None else (BETTER if improved else WORSE)
        fig.add_trace(go.Scatter(x=[off, on], y=[0, 0], mode="lines", line=dict(color=color, width=3), 
                                 hoverinfo="skip", showlegend=False), row=i, col=1)

        left_is_on = on < off
        fig.add_trace(go.Scatter(
            x=[off, on], y=[0, 0], mode="markers+text", showlegend=False,
            marker=dict(size=12, color=[MUTED, MAPLE], line=dict(color=NAVY, width=1)),
            text=[f"Off: {stats.fmt(off, m)}", f"On: {stats.fmt(on, m)}"],
            textposition=["middle right" if left_is_on else "middle left", "middle left" if left_is_on else "middle right"],
            textfont=dict(color=[MUTED, TEXT], size=12),
            hovertemplate="%{text}<extra></extra>"), row=i, col=1)
        pad = max(abs(on - off) * 1.6, abs(on) * 0.015, 1e-6)
        fig.update_xaxes(range=[min(on, off) - pad, max(on, off) + pad], visible=False, row=i, col=1)
        fig.update_yaxes(visible=False, range=[-1, 1], row=i, col=1)
        dom = fig.layout[f"yaxis{i if i > 1 else ''}"].domain
        fig.add_annotation(text=stat.label, x=0, xref="paper", xanchor="right", y=(dom[0] + dom[1]) / 2, yref="paper",
                            showarrow=False, font=dict(color=TEXT, size=13), xshift=-10)
    fig.update_layout(height=height_per_metric * n + 24, margin=dict(l=96, r=8, t=8, b=8),
                plot_bgcolor="rgba(0,0,0,0)")
    return fig

def _arc(cx, cy, r, theta1, theta2, n=60):
    t = np.linspace(np.radians(theta1), np.radians(theta2), n)
    return cx + r * np.cos(t), cy + r * np.sin(t)

def draw_court(fig, color=LINE):
    def line(x, y, dash=None):
        fig.add_trace(go.Scatter(x=list(x), y=list(y), mode="lines", hoverinfo="skip", 
                      showlegend=False, line=dict(color=color, width=1.5, dash=dash)))

    line(*_arc(0, 0, 7.5, 0, 360)) # hoop
    line([-30, 30], [-7.5, -7.5]) # backboard
    line([-80, -80, 80, 80], [-47.5, 142.5, 142.5, -47.5]) # paint
    line([-60, -60, 60, 60], [-47.5, 142.5, 142.5, -47.5]) 
    line(*_arc(0, 142.5, 60, 0, 180)) # free throw circle
    line(*_arc(0, 142.5, 60, 180, 360), dash="dash")
    line(*_arc(0, 0, 40, 0, 180))
    line([-220, -220], [-47.5, 92.5])
    line([220, 220], [-47.5, 92.5])
    line(*_arc(0, 0, 237.5, 22, 158))
    line(*_arc(0, 422.5, 60, 180, 360))
    line([-250, -250, 250, 250, -250], [-47.5, 422.5, 422.5, -47.5, -47.5])
    fig.update_xaxes(range=[-252, 252], visible=False)
    fig.update_yaxes(range=[-52, 300], visible=False, scaleanchor="x", scaleratio=1)
    return fig

def diff_goodness(diff, better: bool | None, scale):
    '''Maps a difference from average on a 0-1 scale: +scale or better is fully green.'''
    if diff is None or pd.isna(diff) or better is None:
        return None 
    signed = diff if better else -diff 
    return min(max(0.5 + signed / (2 * scale), 0.0), 1.0)

def _pct_axis(key):
    fmt = stats.get(key).fmt
    return {"tickformat": ".0%"} if fmt == "pct" else {}

def shot_chart(shots, height=460):
    '''Every shot on a half court: makes in maple, misses as muted crosses.'''
    fig = go.Figure()
    draw_court(fig)
    for made, name, marker in (
        (0, "Missed", dict(symbol="x-thin", size=6, color=MUTED, opacity=0.55, line=dict(width=1.2, color=MUTED))),
        (1, "Made", dict(symbol="circle", size=6, color=MAPLE, opacity=0.8, line=dict(width=0)))
    ):
        d = shots[shots['shot_made_flag'] == made]
        fig.add_trace(go.Scatter(
            x=d['loc_x'], y=d['loc_y'], mode="markers", name=name, marker=marker,
            customdata=np.stack([d.get('action_type', pd.Series("", index=d.index)).astype(str),
                                 d.get('shot_distance', pd.Series(np.nan, index=d.index))], axis=-1) if len(d) else None,
            hovertemplate=f"{name}: %{{customdata[0]}}, %{{customdata[1]}} ft<extra></extra>"
        ))

    fig.update_layout(height=height, margin=dict(l=0, r=0, t=8, b=0),
                      legend=dict(orientation="h", y=0.02, x=0.5, xanchor="center", yanchor="top"))
    return fig 

def zone_chart(zones, height=300):
    '''FG% by zone mnus the league's FG% from the same spots, with volume labeled.'''
    z = zones.groupby('shot_zone_basic').apply(
        lambda d: pd.Series({"fga": d.fga.sum(), "fgm": d.fgm.sum(), "lg": np.average(d.league_avg_fg_pct.fillna(0), weights=d.fga) if d.fga.sum() else np.nan}),
        include_groups=False).reindex(ZONE_ORDER).dropna(subset=["fga"])

    z = z[z.fga > 0]
    total = z.fga.sum()
    z["fg_pct"] = z.fgm / z.fga
    z["diff"] = z.fg_pct - z.lg
    labels = [f"<b>{ZONE_LABELS.get(i, i)}</b><br><span style='color:{MUTED}'>{p:.1%} on {int(n)} FGA, {n / total:.0%} of total FGA</span>"
              for i, p, n in zip(z.index, z.fg_pct, z.fga)]
    fig = go.Figure(go.Bar(
        y=labels, x=z['diff'], orientation="h",
        marker=dict(color=[goodness_color(diff_goodness(d, True, 0.08)) for d in z["diff"]]),
        text=[f"{d * 100:+.1f}" for d in z["diff"]], textposition="outside", cliponaxis=False,
        customdata=z.lg, hovertemplate="%{x:+.1%} vs league (league %{customdata:.1%})<extra></extra>"
    ))
    span = max(abs(z["diff"]).max() if len(z) else 0.05, 0.04) * 1.35
    fig.add_vline(x=0, line_color=MUTED, line_width=1)
    fig.update_layout(height=max(height, 58 * len(z) + 70),
                      xaxis=dict(range=[-span, span], tickformat="+.0%", title="FG% vs League from the same zone"),
                      yaxis=dict(autorange="reversed"), margin=dict(l=8, r=8, t=8 ,b=8), bargap=0.35)
    return fig

def play_type_chart(df, defensive=False, min_poss=10):
    '''Frequency of each play type. Bar color shows ppp vs league'''
    d = df[df['possessions'] >= min_poss].sort_values('frequency', ascending=True)
    better = not defensive
    colors = [goodness_color(diff_goodness(v, better, 0.15)) for v in d['ppp_vs_league']]
    verb = "allowed" if defensive else ""
    fig = go.Figure(go.Bar(
        y=d["play_type_label"], x=d["frequency"], orientation="h", marker=dict(color=colors),
        text=[f"{p:.2f} PPP {verb} vs {lg:.2f}".replace(' ', ' ') for p, lg in zip(d['ppp'], d['league_ppp'])],
        textposition="outside", cliponaxis=False, customdata=np.stack([d['possessions'], d['ppp'], d['league_ppp']], axis=-1),
        hovertemplate="%{y}: %{x:.1%} of possessions (%{customdata[0]:.0f})<br>"
                      "%{customdata[1]:.2f} points per possession, league %{customdata[2]:.2f}<extra></extra>"
    ))
    top = d["frequency"].max() if len(d) else 0.3
    fig.update_layout(height=34 * max(len(d), 1) + 60, xaxis=dict(tickformat=".0%", range=[0, top * 1.7], title="Share of possessions"),
                      margin=dict(l=8, r=8, t=8, b=8))

    return fig

def dot_compare(labels, actual, expected, key, actual_name="Allowed", expected_name="Expected", better=False):
    '''Two values per row on one shared axis, joined by a line colored by whether actual beats expected.'''
    fig = go.Figure()
    for i, (lab, a, e) in enumerate(zip(labels, actual, expected)):
        if pd.isna(a) or pd.isna(e):
            continue 
        good = None if better is None else ((a > e) == better)
        fig.add_trace(go.Scatter(x=[e, a], y=[lab, lab], mode="lines", showlegend=False, hoverinfo="skip",
                                 line=dict(color=NEUTRAL if good is None else (BETTER if good else WORSE), width=3)))
    fig.add_trace(go.Scatter(x=expected, y=labels, mode="markers", name=expected_name,
                            marker=dict(size=11, color=NAVY, line=dict(color=MUTED, width=2)),
                            hovertemplate=f"{expected_name}: %{{x:.1%}}<extra></extra>"))
    fig.add_trace(go.Scatter(x=actual, y=labels, mode="markers", name=actual_name, marker=dict(size=12, color=MAPLE),
                             hovertemplate=f"{actual_name}: %{{x:.1%}}<extra></extra>"))
    fig.update_layout(height=46 * len(labels) + 70, xaxis=_pct_axis(key), yaxis=dict(autorange="reversed"),
                      legend=dict(orientation="h", y=1.08, x=1, xanchor="right"), margin=dict(l=8, r=8, t=30, b=8))

    return fig 

def game_trend(games, y, window=10, height=300):
    '''Each game as a bar with the rolling average in maple and the season average dashed.'''
    g = games.sort_values("game_date")
    roll = g[y].rolling(window, min_periods=max(3, window // 3)).mean()
    stat = stats.get(y)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=g['game_date'], y=g[y], name="Game", marker=dict(color=NEUTRAL), opacity=0.7,
                         hovertemplate="%{x|%b %d}: %{y:.1f}<extra></extra>" if stat.fmt != "pct" else "%{x|%b %d}: %{y:.1%}<extra></extra>"))
    fig.add_trace(go.Scatter(x=g['game_date'], y=roll, name=f"{window}-game average", mode="lines", 
                             line=dict(color=MAPLE, width=2.5), hoverinfo="skip"))
    fig.add_hline(y=g[y].mean(), line_dash="dot", line_color=MUTED, line_width=1,
                  annotation_text="Season Average", annotation_font_color=MUTED, annotation_position="top left")
    fig.update_layout(height=height, yaxis=dict(title=stat.label, **_pct_axis(y)), bargap=0.15,
                      legend=dict(orientation="h", y=1.1, x=1, xanchor="right"))
    return fig 

def team_landscape(df, highlight=None, height=560):
    '''Offensive vs Defensive Ratings'''
    fig = go.Figure(go.Scatter(
        x = df['offensive_rating'], y=df['defensive_rating'], mode='markers+text', marker=dict(size=44, opacity=0),
        text=df['team_name'].str.split().str[-1], textposition="bottom center", textfont=dict(color=MUTED, size=11),
        customdata=df['team_id'], hovertext=df['team_name'], hovertemplate="%{hovertext}<br>ORTG %{x:.1f}, DRTG %{y:.1f}<extra></extra>"
    ))
    xr = df['offensive_rating'].max() - df['offensive_rating'].min()
    yr = df['defensive_rating'].max() - df['defensive_rating'].min()
    for r in df.itertuples():
        fig.add_layout_image(dict(source=team_logo_url(r.team_id), x=r.offensive_rating, y=r.defensive_rating,
                                  xref="x", yref="y", sizex=max(xr, 1) * 0.11, sizey=max(yr, 1) * 0.11,
                                  xanchor="center", yanchor="middle", layer="above", opacity=1 if highlight in (None, r.team_id) else 0.35))
    mx, my = df['offensive_rating'].mean(), df['defensive_rating'].mean()
    fig.add_vline(x=mx, line_dash="dot", line_color=MUTED, line_width=1)
    fig.add_hline(y=my, line_dash="dot", line_color=MUTED, line_width=1)
    pad_x, pad_y = max(xr, 1) * 0.15, max(yr, 1) * 0.15
    x0, x1 = df['offensive_rating'].min() - pad_x, df['offensive_rating'].max() + pad_x 
    y0, y1 = df['defensive_rating'].min() - pad_y, df['defensive_rating'].max() + pad_y
    for x, y, txt, xa in ((x1, y0, "Good Offense, Good Defense", "right"), (x0, y0, "Good Defense Only", "left"),
                          (x1, y1, "Good Offense Only", "right"), (x0, y1, "Below Average Offense and Defense", "left")):
        fig.add_annotation(x=x, y=y, text=txt, showarrow=False, xanchor=xa, font=dict(color=MUTED, size=12))
    fig.update_layout(height=height, xaxis=dict(title="Offensive Rating", range=[x0, x1]), margin=dict(l=8, r=8, t=16, b=8))
    fig.update_layout(height=height, yaxis=dict(title="Defensive Rating", range=[y1, y0]), margin=dict(l=8, r=8, t=16, b=8))

    return fig

def percentile_compare(rows, name_a, name_b):
    '''Two subject's percentiels per stat; maple is the first subject'''
    labels = [r[0] for r in rows]
    a = [None if pd.isna(r[1]) else r[1] * 100 for r in rows]
    b = [None if pd.isna(r[2]) else r[2] * 100 for r in rows]
    fig = go.Figure()
    for lab, va, vb in zip(labels, a, b):
        if va is not None and vb is not None:
            fig.add_trace(go.Scatter(x=[va, vb], y=[lab, lab], mode="lines", line=dict(color=LINE, width=3),
                                     showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=b, y=labels, mode="markers", name=name_b, marker=dict(size=13, color=ACCENT_2),
                  hovertemplate=f"{name_b}: %{{x:.0f}}th percentile<extra></extra>"))
    fig.add_trace(go.Scatter(x=a, y=labels, mode="markers", name=name_a, marker=dict(size=13, color=MAPLE),
                      hovertemplate=f"{name_a}: %{{x:.0f}}th percentile<extra></extra>"))
    fig.add_vline(x=50, line_dash="dot", line_color=MUTED, line_width=1)
    fig.update_layout(height=34 * len(rows) + 80, xaxis=dict(range=[0, 100], title="Percentile Amongst Qualified Players",
                                                             tickvals=[0, 25, 50, 75, 100]),
                     yaxis=dict(autorange="reversed"), legend=dict(orientation="h", y=1.06, x=1, xanchor="right"),
                     margin=dict(l=8, r=8, t=30, b=8))
    return fig 

def explorer_scatter(df, x, y, color_col="position_group", highlight=None, height=560):
    '''Dots that represent each player, grouped by color'''
    palette = {"Guard": BETTER, "Forward": "#7FC8A9", "Center": "#C9A0DC"}
    fig = go.Figure()
    highlight = highlight or set()
    for grp, d in df.groupby(df[color_col].fillna("Unknown")):
        fig.add_trace(go.Scatter(
            x=d[x], y=d[y], mode="markers", name=str(grp),
            marker=dict(size=9, color=palette.get(grp, NEUTRAL), opacity=0.75, line=dict(width=0.5, color=NAVY)),
            customdata=np.stack([d['player_id'], d['season'], d['player_name'], d['label']], axis=-1),
            hovertemplate="%{customdata[2]}<br>%{customdata[3]}<br>"
                          f"{stats.label(x)}: %{{x}}<br>{stats.label(y)}: %{{y}}<extra></extra>"
        ))
    hi = df[df['player_id'].isin(highlight)]
    if not hi.empty:
        fig.add_trace(go.Scatter(x=hi[x], y=hi[y], mode="markers+text", name="Highlighted",
                                 marker=dict(size=14, color=MAPLE, line=dict(width=1.5, color=NAVY)),
                                 text=hi["player_name"], textposition="top center", textfont=dict(color=MAPLE),
                                 customdata=np.stack([hi['player_id'], hi['season'], hi['player_name'], hi['label']], axis=-1),
                                 hovertemplate="%{customdata[2]}<br>%{customdata[3]}<extra></extra>"))

    fig.add_vline(x=df[x].median(), line_dash="dot", line_color=MUTED, line_width=1)
    fig.add_hline(y=df[y].median(), line_dash="dot", line_color=MUTED, line_width=1)
    fx, fy = stats.get(x), stats.get(y)
    hover_x = ":.1%" if fx.fmt in ("pct",) else ":.1f"
    hover_y = ":.1%" if fy.fmt in ("pct",) else ":.1f"
    for tr in fig.data:
        if tr.hovertemplate:
            tr.hovertemplate = tr.hovertemplate.replace("%{x}", "%{x" + hover_x + "}").replace("%{y}", "%{y" + hover_y + "}")

    fig.update_layout(height=height, xaxis=dict(title=fx.label, **_pct_axis(x)), yaxis=dict(title=fy.label, **_pct_axis(y)),
                      legend=dict(orientation="h", y=1.06, x=1, xanchor="right"), dragmode="select")
    
    return fig
