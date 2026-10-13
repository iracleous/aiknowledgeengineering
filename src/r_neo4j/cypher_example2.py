# Session A - Example 2: Programmatic Neo4j Data Population
# This script demonstrates how to populate a Neo4j database using Python
# It creates Person and Movie nodes with relationships using LangChain Neo4j integration

from langchain_neo4j import Neo4jGraph
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

# Sample data: People (actors/directors)
people = [
    {"name": "Keanu Reeves"},
    {"name": "Carrie-Anne Moss"},
    {"name": "Lana Wachowski"},
    {"name": "Lilly Wachowski"},
]

# import pandas as pd
# people = pd.read_csv("people.csv").to_dict(orient="records")

movies = [
    {"title": "The Matrix", "year": 1999},
    {"title": "The Matrix Reloaded", "year": 2003},
]

acted_in = [
    {"person": "Keanu Reeves", "movie": "The Matrix"},
    {"person": "Carrie-Anne Moss", "movie": "The Matrix"},
    {"person": "Keanu Reeves", "movie": "The Matrix Reloaded"},
    {"person": "Carrie-Anne Moss", "movie": "The Matrix Reloaded"},
]

# Sample data: Director relationships
directed = [
    {"person": "Lana Wachowski", "movie": "The Matrix"},
    {"person": "Lilly Wachowski", "movie": "The Matrix"},
    {"person": "Lana Wachowski", "movie": "The Matrix Reloaded"},
    {"person": "Lilly Wachowski", "movie": "The Matrix Reloaded"},
]

# Initialize Neo4j connection using LangChain
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
)

# Clear existing data from the database
graph.query("MATCH (n) DETACH DELETE n")

# Create constraints to ensure data integrity (idempotent - won't fail if already exists)
graph.query(
    """
    CREATE CONSTRAINT person_name IF NOT EXISTS
    FOR (p:Person) REQUIRE p.name IS UNIQUE;
    """
)

graph.query(
    """
    CREATE CONSTRAINT movie_title IF NOT EXISTS
    FOR (m:Movie) REQUIRE m.title IS UNIQUE;
    """
)

# Create nodes using MERGE (creates if doesn't exist, does nothing if exists)
# MERGE nodes
# Create Person nodes from the people list
graph.query(
    """
    UNWIND $people AS row
    MERGE (p:Person {name: row.name})
    """,
    params={"people": people},
)

# Create Movie nodes from the movies list
graph.query(
    """
    UNWIND $movies AS row
    MERGE (m:Movie {title: row.title})
    SET m.year = row.year
    """,
    params={"movies": movies},
)

# Create relationships between nodes
# MERGE relationships
# Create ACTED_IN relationships between actors and movies
graph.query(
    """
    UNWIND $rels AS row
    MATCH (p:Person {name: row.person})
    MATCH (m:Movie {title: row.movie})
    MERGE (p)-[:ACTED_IN]->(m)
    """,
    params={"rels": acted_in},
)

# Create DIRECTED relationships between directors and movies
graph.query(
    """
    UNWIND $rels AS row
    MATCH (p:Person {name: row.person})
    MATCH (m:Movie {title: row.movie})
    MERGE (p)-[:DIRECTED]->(m)
""",
    params={"rels": directed},
)

print("Seed data ingested.")  # Confirmation message

# Query to verify the data was created correctly
# Shows all relationships between people and movies
res = graph.query(
    """
    MATCH (p:Person)-[r]->(m:Movie)
    RETURN labels(p)[0] AS PersonLabel, p.name AS Person, type(r) AS Rel, m.title AS Movie, m.year AS Year
    ORDER BY Movie, Rel, Person
    """
)
print(res)
print("-" * 30)

# Refresh the schema cache for LangChain to understand the database structure
graph.refresh_schema()

# Display database schema information (useful for debugging)
print("DB Schema (for your awareness):")
schema_text = graph.schema or ""
print(schema_text)

# Verification queries to check database state
print(graph.query("MATCH (n) RETURN count(n) AS nodes"))              # Total node count (should be > 0)
print(graph.query("CALL db.labels() YIELD label RETURN collect(label) AS labels"))  # All node labels
print(graph.query("CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) AS rels"))  # All relationship types
