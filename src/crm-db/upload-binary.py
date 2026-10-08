"""
How to upload a binary file to Databricks using the Databricks SDK for Python.
This script demonstrates how to upload a local file (data.csv) to a Databricks volume
"""


from pathlib import Path
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

load_dotenv()

client = WorkspaceClient()

# 2. Define paths
local_file = Path("data/data.csv")
volume_path = "/Volumes/data2026acc123456/crm/crmfolder/data.csv"

 
# Open in binary mode and upload the original bytes.
with local_file.open("rb") as binary_file:
    client.files.upload(
        file_path=volume_path,
        contents=binary_file,
        overwrite=True,
    )

print(f"Uploaded {local_file.name} to {volume_path}")




 
 
 