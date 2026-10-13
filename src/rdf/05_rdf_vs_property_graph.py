# 05_rdf_vs_property_graph.py
import networkx as nx
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD

# --------------------------------------------------
# A. Property graph: purchase metadata on an edge
# --------------------------------------------------
pg = nx.MultiDiGraph()

pg.add_node("alice", label="Customer", name="Alice")
pg.add_node("laptop", label="Product", name="Laptop X")

pg.add_edge(
    "alice",
    "laptop",
    key="purchase:001",
    relationship="PURCHASED",
    quantity=2,
    date="2026-10-01",
)

print("PROPERTY GRAPH")

for customer_id, product_id, edge in pg.edges(data=True):
    print(
        pg.nodes[customer_id]["name"],
        edge["relationship"],
        pg.nodes[product_id]["name"],
        "quantity:",
        edge["quantity"],
    )

# --------------------------------------------------
# B. RDF: purchase represented as an entity
# --------------------------------------------------
EX = Namespace("https://example.org/")

rdf = Graph()
rdf.bind("ex", EX)

rdf.add((EX.Alice, RDF.type, EX.Customer))
rdf.add((EX.Alice, EX.name, Literal("Alice")))

rdf.add((EX.LaptopX, RDF.type, EX.Product))
rdf.add((EX.LaptopX, EX.name, Literal("Laptop X")))

# A distinct purchase entity holds transaction metadata.
rdf.add((EX.Purchase001, RDF.type, EX.Purchase))
rdf.add((EX.Purchase001, EX.customer, EX.Alice))
rdf.add((EX.Purchase001, EX.product, EX.LaptopX))
rdf.add((EX.Purchase001, EX.quantity, Literal(2)))
rdf.add((
    EX.Purchase001,
    EX.date,
    Literal("2026-10-01", datatype=XSD.date),
))

# Query the transaction using SPARQL.
query = """
PREFIX ex: <https://example.org/>

SELECT ?customerName ?productName ?quantity
WHERE {
    ?purchase a ex:Purchase ;
              ex:customer ?customer ;
              ex:product ?product ;
              ex:quantity ?quantity .

    ?customer ex:name ?customerName .
    ?product ex:name ?productName .
}
"""

print("\nRDF")

for row in rdf.query(query):
    print(
        str(row.customerName),
        "PURCHASED",
        str(row.productName),
        "quantity:",
        int(row.quantity),
    )

# Show the RDF representation in Turtle syntax.
print("\nRDF AS TURTLE")
print(rdf.serialize(format="turtle"))