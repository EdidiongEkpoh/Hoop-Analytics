'''
Explanation of data source and key terms.
'''
import streamlit as st
from lib import components as ui, queries, stats 

through = queries.data_through()
seasons = queries.seasons()
ui.page_header("About", "Explanation of data sources, transformation, presentation, and key terms")

left, _ = st.columns([3, 1])
with left:
    st.markdown(f'''   
    Hoop Analytics is a NBA stat application that covers NBA regular season and playoffs from {seasons[-1] if seasons else '2020-21'} 
    onward. {f"The latest game in the data was played on {through}" if through else ""} 
    . This is an independent personal project and is not affiliated with the NBA.

    ### Data Source
    All data comes from the NBA's public stats API through the open-source `nba_api` package. This project
    pulled basic/advanced team/player boxscore data, player tracking, shot locations, play types, hustle stats, on/off splits, and more.
    It originates from a Python script that ingests the raw data, and uses dbt to transform the data into marts that this app uses
    to present the data.
    Note: Does not include play-in games.

    ### Key App Components

    **League** shows the season at a glance: the average team pace, efficiency, three point rate, and true shooting
    percentage and how it's changed over the decade. Below that are every team's offensive and defensive ratings
    displayed on a chart, along with the regular seasons standings, league play type efficiency/effectiveness, and
    stat leaders. 

    **Teams** zooms in on one team, its ratings, and how they stacked up to their counterparts. The Four Factors
    (eFG%, turnovers, rebounding, and free throw rate) on both ends are displayed to show how they maximized and
    creaated possessions. Additionally, there's information on how frequent they went to and scored on different play types,
    shot distribution, player impact, season-over-season statistical trends, and a game log.

    **Players** profiles one player. It includes percentile rankings in comparison to qualified players (or their position group),
    their shot chart, shot profile, defense/hustle numbers, on/off data, season-over-season performance, and a game log.

    **Compare** puts two players or teams side by side to compare performance and impact. Percentiles are measured
    within their respective season.

    **Explorer** plots any two stats against each other for one or multiple seasons in the data for position, minutes,
    team and qualification, plus a sortable leaderboard.

    Any player or team name you click opens that profile. The season, season type and stat basis (per game, per 36, per 75, or per 100)
    you choose carry across pages and are saved in the page link.
    
    ### Who Counts as Qualified
    The percentiles, leaderboards, and the Explorer's default view use qualified players only. For a player to be
    qualified in the regular season, they need to play at least 35% of their available games in the season
    while averaging at least 10 minutes per game. In the playoffs, it's at least half of their teams games while
    playing at least 10 minutes per contest. Players below the threshold will still have displayable profiles with
    their measures stacking up against the qualified players.

    ### How to Interpret on/off numbers
    
    The prevalence of on/off numbers as seen a noticeable boom in the past couple of years. This can be attributed to the
    work that the good folks at databallr (an inspiration for this project) have published. On/offs compare a team with
    a player on the court and off of it. It displays differences in stats as broad as net rating, or as narrow (but still consequential)
    as team TOV%. It's not the end all be all in determining how good a player is/was as deeper digging into more stats, film, and overall
    team context is needed to fully grasp a players impact (in my opinion). Watch for the samples of possessions that accompany 
    the on/off to determine the noise of the data.
    ''')

    st.markdown("### Glossary")
    keys = ["ts_pct", "relative_ts_pct", "efg_pct", "fg3pr", "ftr", "usage", "assist_pct", "tov_pct", "reb_pct", "stl_pct",
           "blk_pct", "offensive_rating", "defensive_rating", "net_rating", "pace", "ppp", "overall_fg_pct_diff"]
    st.dataframe([{"Stat": stats.label(k), "Meaning": stats.get(k).desc} for k in keys], hide_index=True, width="stretch",
                  height=35 * (len(keys) + 1) + 3)