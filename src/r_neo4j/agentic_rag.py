"""
Simple Agentic RAG system combining:

1. ChromaDB for semantic vector search
2. Neo4j for structured relationship queries
3. LangChain v1 create_agent()
4. Azure OpenAI for chat and embeddings


ChromaDB -> Stores and searches vectors ->
         Finds historical tickets with similar symptoms
Neo4j -> Stores entities and relationships 
    -> Identifies ownership, responsibilities, severity and expertise

LangChain agent -> Connects the LLM with the search tools -> Automatically decides which business information source to consult

LangChain tools -> Expose controlled operations to the agen -> Give the assistant specific business capabilities


"""

import json
import os
from typing import Any

import chromadb
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_neo4j import Neo4jGraph
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings


load_dotenv()


# =========================================================
# 1. and 2. Initialize Azure OpenAI and Embeddings model
# =========================================================

llm = AzureChatOpenAI(model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")) 

embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
    api_key=os.getenv("AZURE_EMBEDDING_API_KEY"),
    azure_deployment=os.getenv(
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
    ),
    api_version=os.getenv("AZURE_EMBEDDING_API_VERSION"),
)


# =========================================================
# 3. Set up ChromaDB
# =========================================================

# In-memory ChromaDB.
# Replace Client() with PersistentClient(path="./chroma_data")
# if you want the data to survive program restarts.
# now memory database 
chroma_client = chromadb.Client()

collection = chroma_client.get_or_create_collection(
    name="tickets",
    metadata={"hnsw:space": "cosine"},
)

ticket_documents = [
    "App crashes when user tries to log in with a Google account.",
    "User was charged twice for a subscription renewal.",
    "Dashboard loads slowly on mobile devices.",
    "Export feature is not working for PDF files.",
    "Billing notification emails are not being received.",
]

ticket_ids = [
    "T-101",
    "T-102",
    "T-103",
    "T-104",
    "T-105",
]

ticket_metadata = [
    {"source": "ticket-T-101", "category": "authentication"},
    {"source": "ticket-T-102", "category": "billing"},
    {"source": "ticket-T-103", "category": "performance"},
    {"source": "ticket-T-104", "category": "export"},
    {"source": "ticket-T-105", "category": "notifications"},
]


def initialize_chroma() -> None:
    """Create or update the sample documents in ChromaDB."""

    document_embeddings = embeddings.embed_documents(
        ticket_documents
    )

    # upsert() makes initialization idempotent:
    # existing IDs are updated instead of causing duplicate-ID errors.
    collection.upsert(
        ids=ticket_ids,
        documents=ticket_documents,
        metadatas=ticket_metadata,
        embeddings=document_embeddings,
    )


# =========================================================
# 4. Set up Neo4j
# =========================================================

graph = Neo4jGraph(
    url=os.environ["NEO4J_URI"],
    username=os.environ["NEO4J_USER"],
    password=os.environ["NEO4J_PASSWORD"],
    database=os.getenv("NEO4J_DATABASE", "neo4j"),
)


def initialize_neo4j(clear_existing_data: bool = False) -> None:
    """
    Initialize the Neo4j sample graph.

    clear_existing_data=True deletes every node and relationship
    in the configured database. Keep it False in normal usage.
    """

    if clear_existing_data:
        graph.query("MATCH (n) DETACH DELETE n")

    # Create uniqueness constraints.
    graph.query(
        """
        CREATE CONSTRAINT ticket_id_unique IF NOT EXISTS
        FOR (ticket:Ticket)
        REQUIRE ticket.id IS UNIQUE
        """
    )

    graph.query(
        """
        CREATE CONSTRAINT category_name_unique IF NOT EXISTS
        FOR (category:Category)
        REQUIRE category.name IS UNIQUE
        """
    )

    graph.query(
        """
        CREATE CONSTRAINT team_name_unique IF NOT EXISTS
        FOR (team:Team)
        REQUIRE team.name IS UNIQUE
        """
    )

    graph.query(
        """
        CREATE CONSTRAINT developer_name_unique IF NOT EXISTS
        FOR (developer:Developer)
        REQUIRE developer.name IS UNIQUE
        """
    )

    # MERGE makes this operation safe to run repeatedly.
    graph.query(
        """
        MERGE (ticket:Ticket {id: 'T-101'})
        SET ticket.title = 'Login Bug',
            ticket.severity = 'high'

        MERGE (category:Category {name: 'authentication'})
        MERGE (team:Team {name: 'backend'})
        MERGE (developer:Developer {name: 'Alice'})
        SET developer.expertise = 'authentication'

        MERGE (ticket)-[:HAS_CATEGORY]->(category)
        MERGE (ticket)-[:OWNED_BY]->(team)
        MERGE (ticket)-[:ASSIGNED_TO]->(developer)
        """
    )

    graph.query(
        """
        MERGE (ticket:Ticket {id: 'T-102'})
        SET ticket.title = 'Billing Issue',
            ticket.severity = 'critical'

        MERGE (category:Category {name: 'billing'})
        MERGE (team:Team {name: 'payments'})
        MERGE (developer:Developer {name: 'Bob'})
        SET developer.expertise = 'payments'

        MERGE (ticket)-[:HAS_CATEGORY]->(category)
        MERGE (ticket)-[:OWNED_BY]->(team)
        MERGE (ticket)-[:ASSIGNED_TO]->(developer)
        """
    )

    graph.query(
        """
        MERGE (ticket:Ticket {id: 'T-103'})
        SET ticket.title = 'Performance',
            ticket.severity = 'medium'

        MERGE (category:Category {name: 'performance'})
        MERGE (team:Team {name: 'frontend'})
        MERGE (developer:Developer {name: 'Charlie'})
        SET developer.expertise = 'performance'

        MERGE (ticket)-[:HAS_CATEGORY]->(category)
        MERGE (ticket)-[:OWNED_BY]->(team)
        MERGE (ticket)-[:ASSIGNED_TO]->(developer)
        """
    )

    graph.refresh_schema()


# =========================================================
# 5. Helper functions
# =========================================================

def to_json(value: Any) -> str:
    """Serialize database results safely."""

    return json.dumps(
        value,
        indent=2,
        ensure_ascii=False,
        default=str,
    )


def extract_text_from_agent_result(result: dict[str, Any]) -> str:
    """Extract the final assistant text from a LangChain v1 result."""

    final_message = result["messages"][-1]
    content = final_message.content

    if isinstance(content, str):
        return content

    # Some models return structured content blocks.
    if isinstance(content, list):
        text_parts: list[str] = []

        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(str(block.get("text", "")))
            else:
                text_parts.append(str(block))

        return "\n".join(text_parts)

    return str(content)


# =========================================================
# 6. Define agent tools
# =========================================================

@tool
def vector_search(query: str) -> str:
    """
    Search support-ticket descriptions using semantic similarity.

    Use this tool when the request concerns ticket content, symptoms,
    errors or conceptually similar historical incidents.
    """

    try:
        query_embedding = embeddings.embed_query(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            include=["documents", "metadatas", "distances"],
        )

        documents = results.get("documents")
        metadatas = results.get("metadatas")
        distances = results.get("distances")

        if not documents or not documents[0]:
            return "No semantically similar tickets were found."

        matches = []

        for index, document in enumerate(documents[0]):
            metadata = (
                metadatas[0][index]
                if metadatas and metadatas[0]
                else {}
            )

            distance = (
                distances[0][index]
                if distances and distances[0]
                else None
            )

            # With cosine distance:
            # similarity = 1 - distance.
            similarity = (
                round(1 - float(distance), 4)
                if distance is not None
                else None
            )

            matches.append(
                {
                    "document": document,
                    "source": metadata.get("source"),
                    "category": metadata.get("category"),
                    "cosine_similarity": similarity,
                }
            )

        return "Vector search results:\n" + to_json(matches)

    except Exception as exc:
        return f"Vector search failed: {type(exc).__name__}: {exc}"


@tool
def search_ticket_assignments() -> str:
    """
    Return tickets together with their assigned developers and
    developer expertise.

    Use this tool for questions about ownership, responsibility,
    assignments or developer expertise.
    """

    try:
        results = graph.query(
            """
            MATCH (ticket:Ticket)
            OPTIONAL MATCH
                (ticket)-[:ASSIGNED_TO]->(developer:Developer)
            RETURN
                ticket.id AS ticket_id,
                ticket.title AS title,
                developer.name AS developer,
                developer.expertise AS expertise
            ORDER BY ticket.id
            LIMIT 20
            """
        )

        return "Ticket assignment results:\n" + to_json(results)

    except Exception as exc:
        return (
            "Assignment search failed: "
            f"{type(exc).__name__}: {exc}"
        )


@tool
def search_ticket_structure() -> str:
    """
    Return tickets with their categories, owning teams and severity.

    Use this tool for questions about ticket categories, teams,
    severity or structured ticket relationships.
    """

    try:
        results = graph.query(
            """
            MATCH (ticket:Ticket)
            OPTIONAL MATCH
                (ticket)-[:HAS_CATEGORY]->(category:Category)
            OPTIONAL MATCH
                (ticket)-[:OWNED_BY]->(team:Team)
            RETURN
                ticket.id AS ticket_id,
                ticket.title AS title,
                ticket.severity AS severity,
                category.name AS category,
                team.name AS team
            ORDER BY
                CASE ticket.severity
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                    ELSE 5
                END,
                ticket.id
            LIMIT 20
            """
        )

        return "Ticket structure results:\n" + to_json(results)

    except Exception as exc:
        return (
            "Structured graph search failed: "
            f"{type(exc).__name__}: {exc}"
        )


@tool
def combined_ticket_search(query: str) -> str:
    """
    Perform semantic vector search and structured graph searches.

    Use this tool when answering a question requires both similar
    historical ticket content and graph relationships.
    """

    vector_result = vector_search.invoke({"query": query})
    structure_result = search_ticket_structure.invoke({})
    assignment_result = search_ticket_assignments.invoke({})

    return (
        f"{vector_result}\n\n"
        f"{structure_result}\n\n"
        f"{assignment_result}"
    )


# =========================================================
# 7. Create the LangChain v2 agent
# =========================================================

tools = [
    vector_search,
    search_ticket_assignments,
    search_ticket_structure,
    combined_ticket_search,
]

SYSTEM_PROMPT = """
You are a technical-support assistant with access to two data stores:

1. ChromaDB:
   Contains unstructured ticket descriptions and supports semantic
   similarity search.

2. Neo4j:
   Contains structured relationships among tickets, categories,
   teams and developers.

Tool-selection guidelines:

- Use vector_search for symptoms, descriptions and similar incidents.
- Use search_ticket_assignments for developers and assignments.
- Use search_ticket_structure for categories, teams and severity.
- Use combined_ticket_search only when both semantic and structured
  information are necessary.

Base your answer only on evidence returned by the tools.

When information is unavailable, state that clearly. Do not invent ticket
IDs, developers, teams, categories or remediation instructions.

Give concise answers and mention the relevant ticket IDs as evidence.
"""

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
)


# =========================================================
# 8. Run example queries
# =========================================================

def ask_agent(query: str) -> str:
    """Send one user query to the agent."""

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ]
        }
    )

    return extract_text_from_agent_result(result)


def main() -> None:
    initialize_chroma()

    # Change to True only for a disposable/demo Neo4j database.
    initialize_neo4j(clear_existing_data=False)

    test_queries = [
        "Find tickets about login and authentication issues.",
        "Who is assigned to handle billing problems?",
        "Show all tickets with their categories and owning teams.",
    ]

    print("\n" + "=" * 60)
    print("Agentic RAG System – ChromaDB and Neo4j")
    print("=" * 60)

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)

        try:
            answer = ask_agent(query)
            print(f"Answer: {answer}")
        except Exception as exc:
            print(
                "Agent invocation failed: "
                f"{type(exc).__name__}: {exc}"
            )


if __name__ == "__main__":
    main()