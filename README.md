# Hoop Analytics

An end-to-end NBA analytics platform. Built by Python pipeline that pulls data from `nba_api`, 
includes daily in-season refreshes via Airflow, utilizes dbt to transform raw data into layers, and a 
multi-page Streamlit dashboard that features an overview, team, player, and comparison pages.

[Live App](https://hoop-analytics-jekmmdgrkfr8s4by9sjhgv.streamlit.app/)


# Four Pages
- **League Overview** - Season standings, league leaders, and visuals that depict general team/player performance
- **Team Overview** - Four Factors (efg%, REB%, TOV%, FTR) for offense and defense, team rolling net rating, team shot distribution, and player usage
- **Player Overview** - Per game, per 36, per 75/100 possession counting stats with percentiles, shot charts, and scoring type breakdowns
- **Comparison** - side-by-side team and player statistical comparisons across all seasons in DB (2021-2026 as of 9/23/26)

# Scope 
Only features NBA regular season and playoff data from the 2020-21 seasons to the most recent 2025-26 season. WNBA (and maybe even NCAA)
data will be integrated at a later date, which would make the **league** filter more useful.

# Tech Stack
| Layer | Tools |
|---|---|
| Extraction | Python, `nba_api`, `pandas`, `SQLAlchemy` |
| Orchestration | Apache Airflow (Docker) |
| Warehouse | PostgreSQL containerized locally via Docker -> pushed to Neon |
| Transformation | dbt |
| Dashboard | Streamlit (Tableau/Power BI soon) |
| Hosting | Streamlit Community Cloud (Tableau Public soon) |

The pipeline (extraction, Airflow, dbt) rus locally against a Dockerized Postgres wearehouse. The deployed dashboard reads
from a separate Neon instance that holds the dbt layers.

## Getting Started

```bash
git clone <repo-url>
cd hoop-analytics
cp .env.example .env   # fill in your own credentials
docker compose up -d --build
```

Once the containers are healthy, trigger the DAG from the Airflow UI at `http://localhost:8080` (DAG: `hoop_analytics_pipeline`), or run manually:
```bash
docker compose exec airflow-scheduler bash -c \
  "cd /opt/airflow/extract && python3 extract.py --seasons 2025-26 --league 00"
docker compose exec airflow-scheduler bash -c \
  "cd /opt/airflow/dbt && dbt deps --profiles-dir . && dbt run --profiles-dir . && dbt test --profiles-dir ."
```

To run the dashboard locally against your own warehouse:
```bash
cd streamlit
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```
hoop-analytics/
├── docker-compose.yml
├── .env.example
├── airflow/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── dags/hoop_analytics_pipeline.py
├── extract/
│   └── extract.py
├── postgres-init/
│   └── 01-schemas.sql
├── dbt/
│   ├── dbt_project.yml
│   ├── packages.yml
│   ├── profiles.yml
│   ├── macros/
│   ├── models/{staging,intermediate,marts}/
│   └── tests/
└── streamlit/
    ├── app.py
    ├── Home.py
    ├── db.py
    ├── ui.py
    └── pages/
```

# What's Next?
1. Larger backfill of data (from 2016-2020 to start)
2. Adding WNBA
3. More all-in-one metrics like BPM, EPM, and maybe even RAPM
4. Season over season visuals
5. Tableau Dashboard
6. Misc. tweaks to UI

# Inspiration
I love basketball and I love data. Two sites that have blended these two concepts beautifully are databallr ([Site](https://databallr.com/) | [Twitter](https://x.com/databallr))
and Hoopology ([Site](https://hoopologyviz.com/) | [Twitter](https://x.com/Justinpinnix)). I wanted to make a version of my own so that 
I could fully appreciate the lengths that the two creators ventured to 
put togehter their sites, and so that I can keep up with the current hoop landscape as the seasons progress. I'll continue to make updates
to this repo in the hopes of constructing an app half as good as theirs.