'''
'''
import math
from dataclasses import dataclass
import pandas as pd
import streamlit as st

@dataclass(frozen=True)
class Stat:
    label: str 
    fmt: str 
    better: bool | None = True 
    desc: str = ""
    scaled: bool = False

GRAINS = {"Per game": "per_game", "Per 36": "per_36", "Per 75": "per_75", "Per 100": "per_100"}
GRAIN_LABELS = {v: k for k, v in GRAINS.items()}

S = Stat 
STATS: dict[str, Stat] = {
    "games_played": S("GP", "num0", None, "Games played"),
    "wins": S("W", "num0"),
    "minutes_per_game": S("MPG", "num1", None, "Minutes per game"),
    "possessions_per_game": S("Poss/G", "num1", None, "Possessions per game"),

    "pts": S("PTS", "num1", True, "Points", scaled=True),
    "reb": S("REB", "num1", True, "Rebouunds", scaled=True),
    "ast": S("AST", "num1", True, "Assists", scaled=True),
    "stl": S("STL", "num1", True, "Steals", scaled=True),
    "blk": S("BLK", "num1", True, "Blocks", scaled=True),
    "tov": S("TOV", "num1", False, "Turnovers", scaled=True),
    "fgm": S("FGM", "num1", True, "Field goals made", scaled=True),
    "fga": S("FGA", "num1", None, "Field goals attempted", scaled=True),
    "fg2m": S("2PM", "num1", True, "Two point field goals made", scaled=True),
    "fg2a": S("2PA", "num1", None, "Two point field goals attempted", scaled=True),
    "fg3m": S("3PM", "num1", True, "Three point field goals made", scaled=True),
    "fg3a": S("3PA", "num1", None, "Three point field goals attempted", scaled=True),
    "ftm": S("FTM", "num1", True, "Free throws made", scaled=True),
    "fta": S("FTA", "num1", None, "Free throws attempted", scaled=True),
    "oreb": S("OREB", "num1", True, "Offensive rebounds", scaled=True),
    "dreb": S("DREB", "num1", True, "Defensive rebounds", scaled=True),
    "pf": S("PF", "num1", False, "Personal Fouls", scaled=True),
    "plus_minus": S("+/-", "signed1", True, "Raw point differential while on the court", scaled=True),

    "catch_shoot_fgm": S("Catch & Shoot FGM", "num1", True, scaled=True),
    "catch_shoot_fga": S("Catch & Shoot FGA", "num1", None, scaled=True),
    "catch_shoot_fg3m": S("Catch & Shoot 3PM", "num1", True, scaled=True),
    "catch_shoot_fg3a": S("Catch & Shoot 3PA", "num1", None, scaled=True),
    "catch_shoot_fg_pct": S("Catch & Shoot FG%", "pct", True),
    "catch_shoot_fg3_pct": S("Catch & Shoot 3P%", "pct", True),
    "catch_shoot_pts": S("Catch & Shoot PTS", "num1", True, scaled=True),
    "catch_shoot_efg": S("Catch & Shoot eFG%", "pct", True),
    "pullup_fgm": S("Pull Up FGM", "num1", True, scaled=True),
    "pullup_fga": S("Pull Up FGA", "num1", None, scaled=True),
    "pullup_fg3m": S("Pull Up 3PM", "num1", True, scaled=True),
    "pullup_fg3a": S("Pull Up 3PA", "num1", None, scaled=True),
    "pullup_pts": S("Pull Up PTS", "num1", True, scaled=True),
    "pullup_fg_pct": S("Pull Up FG%", "pct", True),
    "pullup_fg3_pct": S("Pull Up 3P%", "pct", True),
    "pullup_efg_pct": S("Pull Up eFG%", "pct", True),
    "drives": S("Drives", "num1", None, scaled=True),
    "drive_fgm": S("Drive FGM", "num1", True, scaled=True),
    "drive_fga": S("Drive FGA", "num1", None, scaled=True),
    "drive_pts": S("Drive PTS", "num1", True, scaled=True),
    "drive_ast": S("Drive AST", "num1", True, scaled=True),
    "drive_tov": S("Drive TOV", "num1", False, scaled=True),
    "drive_fg_pct": S("Drive FG%", "pct", True),
    "post_touches": S("Post Touches", "num1", None, scaled=True),
    "post_touch_fgm": S("Post Up FGM", "num1", True, scaled=True),
    "post_touch_fga": S("Post Up FGA", "num1", None, scaled=True),
    "post_touch_pts": S("Post Up", "num1", True, scaled=True),
    "post_touch_ast": S("Post Up AST", "num1", True, scaled=True),
    "post_touch_tov": S("Post Up TOV", "num1", False, scaled=True),
    "post_touch_fg_pct": S("Post Up FG%", "pct", True),
    "pct_ast_fgm": S("Assisted FGM%", "pct", None, "Share of made field goals that were assisted"),
    "pct_uast_fgm": S("Unassisted FGM%", "pct", None, "Share of made field goals that were unassisted"),
    "pct_uast_3pm": S("Unssisted 3PM%", "pct", None, "Share of made three point field goals that were unassisted"),
    "pct_uast_2pm": S("Unassisted 2PM%", "pct", None, "Share of made two point field goals that were unassisted"),
    "pct_pts_paint": S("Paint PTS%", "pct", None, "Share of made field goals that were in the paint"),


    "fg_pct": S("FG%", "pct", True, "Field goal percentage"),
    "fg2_pct": S("2PT%", "pct", True, "Two-point percentage"),
    "fg3_pct": S("3PT%", "pct", True, "Three-point percentage"),
    "ft_pct": S("FT%", "pct", True, "Free throw percentage"),
    "efg_pct": S("eFG%", "pct", True, "Effective field goal percentage"),
    "ts_pct": S("TS%", "pct", True, "True shooting percentage"),
    "relative_ts_pct": S("rTS%", "pct", True, "Relative true shooting percentage"),
    "ftr": S("FTr", "pct", None, "Free throw attempt rate"),
    "fg3pr": S("3Pr", "pct", True, "Three point attempt rate"),

    "usage": S("USG%", "pct", True, "Usage rate"),
    "assist_pct": S("AST%", "pct", True, "Share of teammates field goals assisted while on court"),
    "tov_pct": S("TOV%", "pct", False, "Turnovers per shooting or turnover possessiosn"),
    "oreb_pct": S("OREB%", "pct", True, "Share of available offensive rebounds grabbed"),
    "dreb_pct": S("DREB%", "pct", True, "Share of available defensive rebounds grabbed"),
    "reb_pct": S("REB%", "pct", True, "Share of available rebounds grabbed"),
    "stl_pct": S("STL%", "pct", True, "Steals per opponent possessions while on the court"),
    "blk_pct": S("BLK%", "pct", True, "Blocks per opponent two-point attempts while on the court"),

    "offensive_rating": S("ORTG", "num1", True, "Points scored per 100 possessions"),
    "defensive_rating": S("DRTG", "num1", False, "Points allowed per 100 possessions"),
    "net_rating": S("Net Rating", "signed1", True, "Point differential per 100 possessions"),
    "pace": S("Pace", "num1", None, "Possessions per 48 minutes"),

    "win_pct": S("Win%", "pct", True),
    "ast_to_tov": S("AST/TOV", "num2", True, "Assist-to-turnover ratio"),
    "home_win_pct": S("Home win%", "pct", True),
    "away_win_pct": S("Away win%", "pct", True),
    "opp_efg_pct": S("Opp eFG%", "pct", False, "Opponent effective field goal percentage"),
    "opp_tov_pct": S("Opp TOV%", "pct", True, "Opponent turnover rate"),
    "opp_ftr": S("Opp FTR", "pct", False, "Opponent free throw rate"),
    "opp_fg3pr": S("Opp 3Pr", "pct", None, "Opponent three point rate"),
    "opp_fg_pct": S("Opp FG%", "pct", False),
    "opp_fg3_pct": S("Opp 3P%", "pct", False),
    "opp_ts_pct": S("Opp TS%", "pct", False),
    "tps_fast_break_share": S("Fast-break share", "pct", None, "Percent of points scored in transition"),
    "pts_paint_share": S("Paint share", "pct", None, "Percent of points scored in the paint"),
    "pts_2nd_chance_share": S("Second-chance chare", "pct", None, "Percent of points scored after offensive rebound"),
    "pts_off_tov_share": S("Off-turnover share", "pct", None, "Percent of points scored off turnovers"),
    "pts_fast_break_per_game": S("Fast break PTS", "num1", None),
    "pts_paint_per_game": S("Paint PTS", "num1", None),
    "pts_2nd_chance_per_game": S("2nd Chance PTS", "num1", None),
    "pts_off_tov_per_game": S("PTS off TOV", "num1", None),

    "ast_pct": S("AST rate", "pct", True, "Share of field goals assisted"),
    "on_possessions": S("Poss on", "num0", None, "Estimated possessions with player on the court"),
    "on_possessions": S("Poss off", "num0", None, "Estimated possessions with player off the court"),
    "on_court_share": S("On-court share", "pct", None, "Share of team minutes played"),

    "frequency": S("Freq", "pct", None, "Share of the player's possessions of this play type"),
    "ppp": S("PPP", True, desc="Points per possession"),
    "league_ppp": S("League Avg PPP", "num2", None),
    "ppp_vs_league": S("PPP vs League", "signed2", True),
    "possessions": S("Poss", "num0", None, "Possessions"),

    "overall_d_fg_pct": S("OPP FG% defended", "pct", False, "Opponents FG% with the player as the closest defender"),
    "overall_fg_pct_diff": S("vs expected", "pct_pts", False, "Opponents FG% when guarded minus usual efficiency"),
    "rim_d_fg_pct": S("Rim FG% allowed", "pct", False, "Opponents FG% with the player as the closest defender"),
    "rim_fg_pct_diff": S("Rim vs expected", "pct_pts", False, "Opponents FG% with the player as the closest defender"),
    "rim_d_fga": S("Rim shots defended", "num0", None),
    "fg3_d_fg_pct": S("3P% allowed", "pct", False),
    "fg3_fg_pct_diff": S("3P vs expected", "pct_pts", False),
    "deflections_per_36": S("Deflections/36", "num1", True),
    "contested_shots_per_36": S("Contests/36", "num1", True),
    "charges_drawn_per_36": S("Charges/36", "num1", True),
    "loose_balls_recovered_per_36": S("Loose balls/36", "num1", True),
    "screen_assists_per_36": S("Screen assists/36", "num1", True),
    "boxouts_per_36": S("Boxouts/36", "num1", True)
}

DIFF_FMT = {"pct": "pct_pts", "num1": "signed1", "num2": "signed2", "num0": "signed1"}

def get(key):
    if key in STATS:
        return STATS[key]
    for prefix, label in (('on_', 'on'), ("off_", "off")):
        if key.startswith(prefix) and key[len(prefix):] in STATS:
            base = STATS(key[len(prefix):])
            return Stat(base.label + label, base.fmt, base.bettter, base.desc)

    if key.endswith("_diff") and key[:-5] in STATS:
        base = STATS[key[:-5]]
        return Stat(base.label + " +/-", DIFF_FMT.get(base.fmt, base.fmt), base.better, base.desc)
    for suffix in GRAINS.values():
        if key.endswith("_" + suffix) and key[: -len(suffix) - 1] in STATS:
            return STATS[key[: -len(suffix) - 1]]

    fmt = "pct" if key.endswith(("_pct", "_efg")) or key.startswith("pct_") else "num1"
    return Stat(key.replace("_", " ").capitalize(), fmt, None)

def column(key, grain):
    return f"{key}_{grain}" if get(key).scaled else key 

def label(key):
    return get(key).label 

def fmt(value, key=None, format_code=None):
    if value is None or (isinstance(value, float) and math.isnan(value)) or value is pd.NA:
        return "-"
    code = format_code or get(key).fmt 
    v = float(value)
    return {
        "pct": f"{v:.1%}",
        "pct_pts": f"{v * 100:+.1f}",
        "num0": f"{v:,.0f}",
        "num1": f"{v:,.1f}",
        "num2": f"{v:,.2f}",
        "signed1": f"{v:+.1f}",
        "signed2": f"{v:+.2f}"
    }.get(code, f"{v}")

_PRINTF = {
    "pct": "%.1f%%", "pct_pts": "%+.1f", "num0": "%d", "num1": "%.1f", "num2": "%.2f", 
    "signed1": "%+.1f", "signed2": "%+.2f"
}

def table_config(df, keys, labels=None, pinned=None):
    labels = labels or {}
    pin = {"pinned": True}
    pinned = set(pinned or [])
    out = df[keys].copy()
    config = {}
    for key in keys:
        stat = get(key)
        name = labels.get(key, stat.label)
        if pd.api.types.is_numeric_dtype(out[key]):
            if key not in STATS and pd.api.types.is_integer_dtype(out[key]):
                config[key] = st.column_config.NumberColumn(name, format="%d")
                continue
            if stat.fmt in ("pct", "pct_pts"):
                out[key] = out[key] * 100 
            config[key] = st.column_config.NumberColumn(name, format=_PRINTF.get(stat.fmt, "%.2f"), help=stat.desc or None)
        else:
            config[key] = st.column_config.TextColumn(name, **(pin if key in pinned else {}))
    return out, config 