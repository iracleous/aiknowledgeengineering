"""

binary text data
"""

import io
from databricks.sdk import WorkspaceClient

# 1. Initialize the WorkspaceClient using your named profile 'p1'
w = WorkspaceClient(profile="p1")

# 2. Define paths
local_file_path = "data/data.csv"
volume_destination_path = "/Volumes/data2026acc123456/crm/crmfolder/data.csv"

print(f"Uploading {local_file_path} as binary to target volume...")

# 3. Read local file in binary mode ("rb") and wrap it into a BytesIO stream
with open(local_file_path, "rb") as f:
    binary_data = io.BytesIO(f.read())
    
    # Upload via the modern Databricks Files API
    w.files.upload(
        file_path=volume_destination_path,
        contents=binary_data,
        overwrite=True
    )

print(f"Successfully uploaded binary file to: {volume_destination_path}")