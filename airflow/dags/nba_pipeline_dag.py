from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
import pendulum

local_tz = pendulum.timezone("America/Denver")
default_args = {
    "owner": "airflow",
    "retries": 1
}

with DAG(
    dag_id="hoop_analytics_pipeline",
    default_args=default_args,
    description="Extract nba_api data, then run and test dbt project.",
    schedule="0 9 * * *",
    start_date=datetime(2026, 10, 21, tzinfo=local_tz),
    catchup=False,
    params={
        "seasons": "2026-27",
        "league": "00",
        "season_type": "Regular Season"
    },
    tags=['hoop-analytics']

) as dag:
    extract_data = BashOperator(
        task_id="extract_data",
        bash_command=(
            "cd /opt/airflow/extract && "
            "python3 extract.py --seasons {{ params.seasons }} "
            "--league {{ params.league }} "
            "--season-type '{{ params.season_type }}' "
            "--incremental"
        )
    )

    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command="cd /opt/airflow/dbt && dbt deps --profiles-dir ."
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && dbt run --profiles-dir ."
    )
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt && dbt test --profiles-dir ."
    )

    extract_data >> dbt_deps >> dbt_run >> dbt_test