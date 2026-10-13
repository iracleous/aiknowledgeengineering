"""
uv add networkx rdflib owlrl

01
file: entities.py

This example demonstrates an in-memory property graph. 
Customer and product are nodes; 
the purchase is an edge with properties.

"""

# 01_entities.py
import networkx as nx

graph = nx.MultiDiGraph()

# Stable IDs identify entities; names are properties.
graph.add_node(
    "customer:001",
    label="Customer",
    name="Alice",
    region="Athens",
)

graph.add_node(
    "product:001",
    label="Product",
    name="Laptop X",
    price=1200.0,
)

graph.add_node(
    "supplier:001",
    label="Supplier",
    name="TechSupply",
)

# Inspect all entities.
for entity_id, properties in graph.nodes(data=True):
    print(entity_id, properties)

# Retrieve one entity.
print("\nCustomer name:", graph.nodes["customer:001"]["name"])

# Find entities belonging to a particular type.
products = [
    entity_id
    for entity_id, properties in graph.nodes(data=True)
    if properties["label"] == "Product"
]

print("Product IDs:", products)