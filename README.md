# Hoop Analytics

An end-to-end NBA analytics platform that covers the 2020-21 through 2025-26 (and counting) seasons. 
Built by Python pipeline that pulls 13 `nba_api` endpoints into a PostgreSQL warehouse, dbt models the
raw data into tested staging, intermediate, and mart layers, and Airflow refreshes everything daily
during the season and publishes the finished marts to Neon, where a six-page Streamlit dashboard reads them. 

[Live App](https://hoop-analytics-qhy32etanpqsvqpxwyjkez.streamlit.app/)


# Main Components
- **League** - Season standings, decade-long scoring and pace trends, a team efficiency quadrant chart (offensive vs defensive rating)
  league-wide play-type mix, and a sortable leaders table with Basic, Advanced, and Tracking stats.
- **Teams** - Four Factors (efg%, REB%, TOV%, FTR) for offense and defense with league rankings, team rolling net rating, team shot distribution, Synergy play types, player on/off splits and usage
- **Players** - Per game, per 36, per 75/100 possession counting stats with percentiles that compare to other players in respective season.   Includes shot charts, play types, defense/hustle stats, on/off impact and statistical influences.
- **Compare** - Side-by-side team and player statistical comparisons across any season in the database.
- **Explorer** - Plot any two stats against each other for the whole league and click through to a player
- **About** - Project summary, key components, and disclaimers

# The Data
| | |
|---|---|
| Seasons | 2020-21 to 2025-26, regular season and playoffs |
| Sources | Game logs, advanced box scores, shot charts, player tracking, hustle, Synergy play types, defense dashboard, on/off splits, team misc stats, standings, rosters |
| Warehouse | ~1.7M rows across 21 mart tables, including 1.37M individual shots and 165K player games |

# How It Works

**Extract.** `extract.py` pulls each endpoint and loads it into the `raw` schema. Every load is an atomic
delete-and-insert scoped to a game, player or team, so reruns never duplicate rows and a failed pull never
leaves an incomplete season in the DB. `--incremental` checks the database for what's already loaded and only
fetches what's new.

**Transform.** dbt builds three layers: `staging` (typed, renamed, deduplicated sources), `intermediate`
(additive season totals) and `marts` (final layer). Every rate (shooting percentages, per-36, per-100,
ratings) is calculated from aggregates sesason totals. Shared logic lives in macros, and models are covered by
uniqueness, not-null and range tests.

**Orchestrate and publish.** An Airflow DAG runs every morning from October to June: extract the regular
season and/or playoffs (depending on the month), `dbt build`, then publish. The publish step only runs if every
dbt test passes. It copies the marts to a holding schema on Neon, checks the row counts, and swaps it in
inside a single transaction.

**Serve.** The Streamlit app shares one filter bar (season, season type, stat grain) across pages and keeps
selections in the URL so any view can be bookmarked. Queries are cached for 24 hours for past seasons and
1 hour for the current one.

# Tech Stack
| Layer | Tools |
|---|---|
| Extraction | Python, `nba_api`, `pandas`, `SQLAlchemy` |
| Warehouse | PostgreSQL (Docker) locally, published to Neon |
| Transformation | dbt (`dbt_utils`) |
| Orchestration | Apache Airflow (Docker Compose) |
| Dashboard | Streamlit, Plotly |
| Hosting | Streamlit Community Cloud |

## Getting Started

```bash
git clone https://github.com/EdidiongEkpoh/Hoop-Analytics.git
cd Hoop-Analytics
cp .env.example .env   # fill in your own credentials
docker compose up -d --build
```

Once the containers are healthy, trigger the DAG from the Airflow UI at `http://localhost:8080`
(DAG: `hoop_analytics_pipeline`), or run the steps manually:

```bash
docker compose exec airflow-scheduler bash -c \
  "cd /opt/airflow/extract && python3 extract.py --seasons 2025-26 --league 00"
docker compose exec airflow-scheduler bash -c \
  "cd /opt/airflow/dbt && dbt deps --profiles-dir . && dbt seed --profiles-dir . && dbt build --profiles-dir ."
docker compose exec airflow-scheduler bash -c \
  "cd /opt/airflow/publish && python3 publish_marts.py"   # optional: copy marts to Neon
```

To run the dashboard locally:

```bash
cd app
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```
Hoop-Analytics/
├── docker-compose.yml
├── .env.example
├── airflow/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── dags/hoop_analytics_pipeline.py
├── extract/
│   └── extract.py
├── publish/
│   └── publish_marts.py          # copies marts to Neon with an atomic schema swap
├── postgres-init/
│   └── 01-schemas.sql
├── dbt/
│   ├── dbt_project.yml
│   ├── packages.yml
│   ├── profiles.yml
│   ├── macros/
│   ├── seeds/
│   ├── models/{staging,intermediate,marts}/
│   └── tests/
└── app/
    ├── app.py                    # navigation and the shared filter bar
    ├── lib/                      # db, queries, stats registry, charts, components
    └── views/                    # league, teams, players, compare, explorer, about
```

# What's Next?
1. Larger backfill of data (2016-17 through 2019-20 to start)
2. More in-depth lineup data and statistical influences for team page.
3. Adding WNBA
3. More all-in-one metrics like BPM, EPM, and maybe even RAPM
4. Tableau dashboard
5. Misc. tweaks to the UI

# Inspiration
I love basketball and I love data. Two sites that have blended these two concepts beautifully are databallr ([Site](https://databallr.com/) | [Twitter](https://x.com/databallr))
and Hoopology ([Site](https://hoopologyviz.com/) | [Twitter](https://x.com/Justinpinnix)). I wanted to make a version of my own so that 
I could fully appreciate the lengths that the two creators ventured to 
put togehter their sites, and so that I can keep up with the current hoop landscape as the seasons progress. 
