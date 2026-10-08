"""Run: pip install requests python-dotenv; python test_databricks_customers.py.
Place .env alongside this file or in a parent directory.
"""
import json
import os
import time

import requests
from dotenv import load_dotenv


def main():
    load_dotenv(override=True)
    host = os.environ['DATABRICKS_HOST'].strip().rstrip('/')
    token = os.environ['DATABRICKS_TOKEN'].strip()
    warehouse_id = os.environ['DATABRICKS_WAREHOUSE_ID'].strip()

    statement = '''
        SELECT customer_id, tenure_days, region, segment,
               total_invoices, total_spent, unpaid_invoices,
               total_calls, total_data_usage, avg_calls,
               total_tickets, complaints, avg_resolution_time,
               campaigns_received, campaigns_clicked, campaign_responses,
               days_since_last_usage, days_since_last_invoice, churn_label
        FROM data2026acc123456.crm.gold_customer_features
        ORDER BY customer_id
        LIMIT 10
    '''

    def check_response(response):
        if not response.ok:
            raise RuntimeError(
                f'HTTP {response.status_code}\nDatabricks response: {response.text}'
            )
        return response.json()

    with requests.Session() as session:
        session.headers['Authorization'] = f'Bearer {token}'
        url = f'{host}/api/2.0/sql/statements'
        result = check_response(session.post(
            url,
            json={
                'warehouse_id': warehouse_id,
                'statement': statement,
                'wait_timeout': '10s',
                'disposition': 'INLINE',
                'format': 'JSON_ARRAY',
            },
            timeout=30,
        ))
        statement_id = result['statement_id']
        deadline = time.monotonic() + 120
        while result['status']['state'] in {'PENDING', 'RUNNING'}:
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f'Statement {statement_id} is still running. '
                    'Check Databricks Query History.'
                )
            time.sleep(1)
            result = check_response(session.get(
                f'{url}/{statement_id}', timeout=30,
            ))

        if result['status']['state'] != 'SUCCEEDED':
            raise RuntimeError(json.dumps(result['status'], indent=2))

        columns = [c['name'] for c in result['manifest']['schema']['columns']]
        chunk = result.get('result', {})
        rows = list(chunk.get('data_array', []))
        while chunk.get('next_chunk_internal_link'):
            chunk = check_response(session.get(
                f"{host}{chunk['next_chunk_internal_link']}", timeout=30,
            ))
            rows.extend(chunk.get('data_array', []))

    print(f'Connection successful. Retrieved {len(rows)} rows.')
    # The REST API may represent numeric values as strings; null stays None.
    for row in rows:
        print(json.dumps(dict(zip(columns, row)), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
