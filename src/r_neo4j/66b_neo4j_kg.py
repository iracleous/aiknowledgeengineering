"""
uv add langchain_neo4j

"""

from dotenv import load_dotenv
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
 
import os
from langchain_openai import AzureChatOpenAI



#############################

def fill_data(graph):
    graph.query("""
        MATCH (n) DETACH DELETE n
        """)
    graph.query("""
        CREATE (t1:Ticket {id: 'T-101', text: 'App crashes on login'})-[:HAS_CATEGORY]->(:Category {name: 'bug'}),
            (t1)-[:ESCALATED_TO]->(:Specialist {name: 'tech-specialist'}),
            (t2:Ticket {id: 'T-102', text: 'Charged twice'})-[:HAS_CATEGORY]->(:Category {name: 'billing'}),
            (t2)-[:ESCALATED_TO]->(:Specialist {name: 'billing-specialist'})
        """)



 
load_dotenv()

# 2. Initialize the Agent
llm = AzureChatOpenAI(model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")) 
 
  
graph = Neo4jGraph(url=os.getenv("NEO4J_URI"),
                    username=os.getenv("NEO4J_USER"), 
                    password=os.getenv("NEO4J_PASSWORD"))



fill_data(graph)


graph.refresh_schema()

qa_chain = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    allow_dangerous_requests=True,
    verbose=True,
)

question =  "Which specialist handled ticket T-101?"
question ="When I give the id do not take into account the case of characters. " \
" incident INC-101 is mentioned by whom?" \
" Also give the corresponding cypher code"

result = qa_chain.invoke({"query": question})
print(result["result"])




