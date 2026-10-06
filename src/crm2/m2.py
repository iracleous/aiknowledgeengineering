from databricks.connect import DatabricksSession
from dotenv import load_dotenv

load_dotenv()


# Initialize session using your exact Azure Databricks host URL
spark = DatabricksSession.builder \
    .serverless() \
    .host("https://adb-7405613839659491.11.azuredatabricks.net") \
    .getOrCreate()

print("Successfully connected to Azure Databricks!")

# 1. Ensure the schema (database) exists and switch to it
spark.sql("CREATE SCHEMA IF NOT EXISTS crm")
spark.sql("USE crm")

# 2. Create the 'crm11' table with sample data
print("Creating and populating table crm11...")
spark.sql("""
    CREATE TABLE IF NOT EXISTS crm13 (
        customer_id INT,
        interaction_date DATE,
        channel STRING,
        amount DOUBLE
    )
""")

# Insert sample data into crm11
spark.sql("""
    INSERT INTO crm13 VALUES 
    (101, '2026-09-01', 'Web', 45.0),
    (102, '2026-09-02', 'Mobile', 120.5),
    (103, '2026-09-03', 'Store', 65.0),
    (104, '2026-09-04', 'Web', 200.0)
""")

# 3. Read from the newly created table using PySpark DataFrame API
table_name = "crm.crm13"
print(f"Reading data from {table_name}...")

df = spark.read.table(table_name)

# 4. Run a sample transformation (filtering transactions with amount > 50)
filtered_df = df.filter(df.amount > 50.0)
print(f"Total CRM interactions with amount > 50: {filtered_df.count()}")

# Display results locally
filtered_df.select("customer_id", "interaction_date", "channel", "amount").show(5, truncate=False)