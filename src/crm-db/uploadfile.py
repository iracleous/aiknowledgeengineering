"""

uploads text data
"""
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

load_dotenv()


# 1. Initialize the WorkspaceClient using your named profile 'p1'
w = WorkspaceClient()

# 2. Define your local file path and the target Unity Catalog Volume path
local_file_path = "data/data.csv"  # Replace with your actual local file
volume_destination_path = "/Volumes/data2026acc123456/crm/crmfolder/local_file.csv"

print(f"Uploading {local_file_path} to target volume...")

# 3. Open the local file and upload it using dbutils filesystem utility via SDK
with open(local_file_path, "r") as f:
    w.dbutils.fs.put(
        file=volume_destination_path,
        contents=f.read(),
        overwrite=True
    )

print(f"Successfully uploaded file to: {volume_destination_path}")

# Optional: Verify it exists by listing the volume contents
print("Listing files in volume folder:")
for file_info in w.dbutils.fs.ls("/Volumes/data2026acc123456/crm/crmfolder"):
    print(f" - {file_info.name} ({file_info.size} bytes)")