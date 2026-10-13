import os
from pathlib import Path

from dotenv import load_dotenv
from databricks.sdk import WorkspaceClient

load_dotenv()

client = WorkspaceClient(
    host=f"https://{os.environ['DATABRICKS_SERVER_HOSTNAME']}",
    client_id=os.environ["DATABRICKS_CLIENT_ID"],
    client_secret=os.environ["DATABRICKS_CLIENT_SECRET"],
    auth_type="oauth-m2m",
)

# Requests authentication headers without printing the token.
client.config.authenticate()
print("OAuth authentication succeeded.")