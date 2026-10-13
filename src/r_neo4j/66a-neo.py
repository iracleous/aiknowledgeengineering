"""
uv add langchain_neo4j

"""

from dotenv import load_dotenv
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
 
import os
from langchain_openai import AzureChatOpenAI

from langchain_core.documents import Document
from langchain_neo4j import LLMGraphTransformer

#############################


 
load_dotenv()

# 2. Initialize the Agent
llm = AzureChatOpenAI(model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")) 
 
graph = Neo4jGraph(url="bolt://localhost:7687", username="neo4j", password="codehubpassword")



# ---------------------------------------------------------
# 3. Provide your own unstructured data
# ---------------------------------------------------------

text = """
Incident INC-101 occurred on 20 September 2026.

The Payment API returned HTTP 503 errors and affected multiple customers.
The Payment API runs on the server PROD-WEB-01.

The Payment API depends on the Payments PostgreSQL database.
The database runs on server PROD-DB-01.

Maria Papadopoulou investigated the incident.
She discovered that the database connection pool was exhausted.

Maria restarted the Payment API and increased the maximum connection
pool size. This resolved incident INC-101.
"""




text2 = """
this is the text for 102 bub
jjhj
Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere 
cubilia curae; Sed ac ultricies nisi. Nulla vitae vulputate erat. Donec
 sit amet nisi eget velit imperdiet mollis eget vitae arcu. Nullam lobortis
   vehicula libero. Nam porttitor nulla at sollicitudin luctus. Pellentesque 
   vel vulputate nibh, eu placerat lorem.

Sed rhoncus, ante placerat tincidunt aliquam, sapien lorem vehicula erat,
 in varius massa lectus vitae mauris. Vestibulum ante ipsum primis in faucibus
   orci luctus et ultrices posuere cubilia curae; Vivamus ornare mi nec convallis 
   feugiat. Nulla eu dui ante. Sed fermentum viverra lectus, ac imperdiet arcu. 
   Quisque ut aliquam dui, eget mollis ante. Nunc vel lectus nec lacus posuere
     efficitur quis et enim. Proin mollis bibendum nunc, viverra rhoncus tellus
       porta a.

"""

documents = [
    Document(
        page_content=text,
        metadata={
            "source": "incident-report-101.txt",
            "department": "IT Operations",
        },
    ),
      Document(
            page_content=text2,
            metadata={
                "source": "bug-report-102.txt",
                "department": "IT Operations",
            },
        )
]


# ---------------------------------------------------------
# 4. Convert the text into graph data using the LLM
# ---------------------------------------------------------

transformer = LLMGraphTransformer(llm=llm)

graph_documents = transformer.convert_to_graph_documents(documents)


# ---------------------------------------------------------
# 5. Inspect what the LLM extracted
# ---------------------------------------------------------

for graph_document in graph_documents:
    print("\nNODES")

    for node in graph_document.nodes:
        print(
            f"ID: {node.id}, "
            f"Type: {node.type}, "
            f"Properties: {node.properties}"
        )

    print("\nRELATIONSHIPS")

    for relationship in graph_document.relationships:
        print(
            f"{relationship.source.id} "
            f"-[{relationship.type}]-> "
            f"{relationship.target.id}"
        )


# ---------------------------------------------------------
# 6. Insert the extracted graph into Neo4j
# ---------------------------------------------------------

graph.add_graph_documents(
    graph_documents,
    include_source=True,
    baseEntityLabel=True,
)

print("\nGraph data successfully added to Neo4j.")


# ---------------------------------------------------------
# 7. Refresh and print the Neo4j schema
# ---------------------------------------------------------

graph.refresh_schema()

print("\nNEO4J SCHEMA")
print(graph.schema)