"""
connect to Databricks using PAT
instead of using connection with my credentials


Settings->User->Developer->Access Tokens

Service principal
""" 
 
from databricks.connect import DatabricksSession
import os
from dotenv import load_dotenv
 
load_dotenv()


def get_spark_session():
    # DatabricksSession automatically reads DATABRICKS_HOST and DATABRICKS_CLIENT_ID/SECRET
    # or DATABRICKS_TOKEN from the environment.
    return DatabricksSession.builder.serverless().getOrCreate()

 
def main():
    spark = get_spark_session()
    df = spark.read.table("crm.crm11")
    count = df.count()
    return {
        "message": "Connected to Azure Databricks Serverless!",
        "row_count": count}


result = main()
print(result)
