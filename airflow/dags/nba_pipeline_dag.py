'''
Daily Hoop Analytics Refresh

    in_season -> extract_regular_season -> extract_playoffs -> dbt_deps -> dbt_seed -> dbt_build -> publish_to_neon

Extract and dbt work with the local data warehouse. Only after dbt has built and tested
every model does publish_to_neon copy the marts schema to Neon (NEON_DATABASE_URL),
where the Streamlit app reads it. A failed dbt build or test stops the run before it
reaches the live application. A partly failed extract does not; its loads are atomic,
meaning the run goes on with the data it has, and the failed task shoes red. 
'''

import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import ShortCircuitOperator

REGULAR_SEASON_MONTHS = {10, 11, 12, 1, 2, 3, 4}
PLAYOFF_MONTHS = {4, 5, 6}
local_tz = pendulum.timezone("America/Denver")


def nba_season(dt):
    '''The NBA season a date falls in.'''
    start = dt.year if dt.month >= 7 else dt.year - 1
    return f"{start}-{str(start + 1)[-2:]}"

def in_season(data_interval_end, **_):
    '''Skip the whole run July through September, when they're no NBA games.'''
    month = data_interval_end.in_timezone(local_tz).month
    return month in REGULAR_SEASON_MONTHS | PLAYOFF_MONTHS

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=15)
}


with DAG(
    dag_id="hoop_analytics_pipeline",
    default_args=default_args,
    description="Extract nba_api data, then run and test dbt project.",
    schedule="0 9 * * *",
    start_date=datetime(2026, 10, 21, tzinfo=local_tz),
    catchup=False,
    max_active_runs=1,
    params={
        "seasons": "",
        "league": "00",
    },
    user_defined_macros={"nba_season": nba_season, "local_tz": local_tz},
    tags=['hoop-analytics']

) as dag:

    SEASON = "{{ params.season or nba_season(data_interval_end.in_timezone(local_tz)) }}"
    MONTH = "data_interval_end.in_timezone(local_tz).month"
    EXTRACT = (
        "cd /opt/airflow/extract && python3 extract.py --seasons " + SEASON + 
        " --league {{ params.league}} --incremental --season-type"
    )
    check_season = ShortCircuitOperator(task_id="in_season", python_callable=in_season)

    extract_regular = BashOperator(
        task_id='extract_regular_season',
        bash_command=(
            "{% if " + MONTH + " in " + str(sorted(REGULAR_SEASON_MONTHS)) + " %}"
            + EXTRACT + " 'Regular Season'"
            + "{% else %}echo 'Regular season is over; nothing to extract.'{% endif %}"
        ),
        execution_timeout=timedelta(hours=2)
    )
    extract_playoffs = BashOperator(
        task_id="extract_playoffs",
        bash_command=(
            "{% if " + MONTH + " in " + str(sorted(PLAYOFF_MONTHS)) + " %}"
            + EXTRACT + " 'Playoffs'"
            + "{% else %}echo 'Not the playoffs, yet; nothing to extract.'{% endif %}"
        ),
        execution_timeout=timedelta(hours=1),
        trigger_rule="all_done"
    )

    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command="cd /opt/airflow/dbt && dbt deps --profiles-dir .",
        trigger_rule="all_done"
    )
    dbt_seed = BashOperator(
            task_id="dbt_seed",
            bash_command="cd /opt/airflow/dbt && dbt seed --profiles-dir .",
            
        )
    
    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command="cd /opt/airflow/dbt && dbt build --profiles-dir .",
        execution_timeout=timedelta(hours=1)
    )

    publish = BashOperator(
        task_id="publish_to_neon",
        bash_command="cd /opt/airflow/publish && python3 publish_marts.py",
        execution_timeout=timedelta(minutes=45)
    )

    check_season >> extract_regular >> extract_playoffs >> dbt_deps >> dbt_seed >> dbt_build >> publish