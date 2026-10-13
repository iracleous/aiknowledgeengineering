"""FastAPI service over the Databricks gold_customer_features table.

Install: pip install fastapi uvicorn requests python-dotenv
Run:     python fastapi-gold.py
   or:   uvicorn fastapi-gold:app --reload
Docs:    http://127.0.0.1:8000/docs

Place a .env file (DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_WAREHOUSE_ID)
alongside this file or in a parent directory.
"""
import os
import time
from typing import Any

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query

load_dotenv(override=True)

TABLE = 'data2026acc123456.crm.gold_customer_features'
COLUMNS = '''
    customer_id, tenure_days, region, segment,
    total_invoices, total_spent, unpaid_invoices,
    total_calls, total_data_usage, avg_calls,
    total_tickets, complaints, avg_resolution_time,
    campaigns_received, campaigns_clicked, campaign_responses,
    days_since_last_usage, days_since_last_invoice, churn_label
'''

INT_TYPES = {'BYTE', 'SHORT', 'INT', 'LONG'}
FLOAT_TYPES = {'FLOAT', 'DOUBLE', 'DECIMAL'}

app = FastAPI(title='Gold Customer Features API', version='1.0.0')


def get_config() -> dict[str, str]:
    try:
        return {
            'host': os.environ['DATABRICKS_HOST'].strip().rstrip('/'),
            'token': os.environ['DATABRICKS_TOKEN'].strip(),
            'warehouse_id': os.environ['DATABRICKS_WAREHOUSE_ID'].strip(),
        }
    except KeyError as exc:
        raise HTTPException(
            status_code=500,
            detail=f'Missing environment variable: {exc.args[0]}',
        )


def check_response(response: requests.Response) -> dict:
    if not response.ok:
        raise HTTPException(
            status_code=502,
            detail=f'Databricks HTTP {response.status_code}: {response.text}',
        )
    return response.json()


def convert_value(value: Any, type_name: str) -> Any:
    """The REST API returns numerics as strings; convert them back."""
    if value is None:
        return None
    type_name = type_name.upper()
    try:
        if type_name in INT_TYPES:
            return int(value)
        if type_name in FLOAT_TYPES:
            return float(value)
        if type_name == 'BOOLEAN':
            return str(value).lower() == 'true'
    except (TypeError, ValueError):
        pass
    return value


def run_query(
    statement: str,
    parameters: list[dict] | None = None,
    timeout_seconds: int = 120,
) -> list[dict]:
    cfg = get_config()
    url = f"{cfg['host']}/api/2.0/sql/statements"

    payload: dict[str, Any] = {
        'warehouse_id': cfg['warehouse_id'],
        'statement': statement,
        'wait_timeout': '10s',
        'disposition': 'INLINE',
        'format': 'JSON_ARRAY',
    }
    if parameters:
        payload['parameters'] = parameters

    try:
        with requests.Session() as session:
            session.headers['Authorization'] = f"Bearer {cfg['token']}"

            result = check_response(session.post(url, json=payload, timeout=30))
            statement_id = result['statement_id']
            deadline = time.monotonic() + timeout_seconds

            while result['status']['state'] in {'PENDING', 'RUNNING'}:
                if time.monotonic() >= deadline:
                    raise HTTPException(
                        status_code=504,
                        detail=(
                            f'Statement {statement_id} is still running. '
                            'Check Databricks Query History.'
                        ),
                    )
                time.sleep(1)
                result = check_response(session.get(
                    f'{url}/{statement_id}', timeout=30,
                ))

            if result['status']['state'] != 'SUCCEEDED':
                raise HTTPException(status_code=502, detail=result['status'])

            schema = result['manifest']['schema']['columns']
            names = [c['name'] for c in schema]
            types = [c.get('type_name', 'STRING') for c in schema]

            chunk = result.get('result', {})
            rows = list(chunk.get('data_array', []))
            while chunk.get('next_chunk_internal_link'):
                chunk = check_response(session.get(
                    f"{cfg['host']}{chunk['next_chunk_internal_link']}",
                    timeout=30,
                ))
                rows.extend(chunk.get('data_array', []))
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502, detail=f'Databricks connection error: {exc}',
        )

    return [
        {n: convert_value(v, t) for n, v, t in zip(names, row, types)}
        for row in rows
    ]


@app.get('/health')
def health() -> dict:
    """Checks the Databricks connection with a trivial query."""
    run_query('SELECT 1 AS ok')
    return {'status': 'ok'}


@app.get('/customers')
def list_customers(
    limit: int = Query(10, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> dict:
    """Returns customers ordered by customer_id."""
    # limit/offset are validated integers, so safe to embed in the statement.
    statement = f'''
        SELECT {COLUMNS}
        FROM {TABLE}
        ORDER BY customer_id
        LIMIT {limit} OFFSET {offset}
    '''
    rows = run_query(statement)
    return {'count': len(rows), 'limit': limit, 'offset': offset, 'data': rows}


@app.get('/customers/{customer_id}')
def get_customer(customer_id: str) -> dict:
    """Returns a single customer by id."""
    statement = f'''
        SELECT {COLUMNS}
        FROM {TABLE}
        WHERE customer_id = :customer_id
        LIMIT 1
    '''
    rows = run_query(
        statement,
        parameters=[{'name': 'customer_id', 'value': customer_id}],
    )
    if not rows:
        raise HTTPException(status_code=404, detail='Customer not found')
    return rows[0]


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=8000)
