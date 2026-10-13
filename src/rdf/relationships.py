"""

02
file: src/rdf/relationships.py
"""

# 02_relationships.py
import networkx as nx

graph = nx.MultiDiGraph()

graph.add_node("customer:001", label="Customer", name="Alice")
graph.add_node("product:001", label="Product", name="Laptop X")
graph.add_node("product:002", label="Product", name="Mouse Y")
graph.add_node("supplier:001", label="Supplier", name="TechSupply")

# Customer -> Product
graph.add_edge(
    "customer:001",
    "product:001",
    key="purchase:001",
    relationship="PURCHASED",
    quantity=1,
    date="2026-10-01",
)

graph.add_edge(
    "customer:001",
    "product:002",
    key="purchase:002",
    relationship="PURCHASED",
    quantity=2,
    date="2026-10-02",
)

# Product -> Supplier
graph.add_edge(
    "product:001",
    "supplier:001",
    relationship="SUPPLIED_BY",
)

graph.add_edge(
    "product:002",
    "supplier:001",
    relationship="SUPPLIED_BY",
)

# Query: what did Alice purchase?
print("Alice purchased:")

for _, product_id, edge in graph.out_edges(
    "customer:001", data=True
):
    if edge["relationship"] == "PURCHASED":
        print(
            graph.nodes[product_id]["name"],
            "quantity:",
            edge["quantity"],
        )

# Two-hop query: which suppliers supplied Alice's purchases?
supplier_names = set()

for _, product_id, purchase in graph.out_edges(
    "customer:001", data=True
):
    if purchase["relationship"] != "PURCHASED":
        continue

    for _, supplier_id, relationship in graph.out_edges(
        product_id, data=True
    ):
        if relationship["relationship"] == "SUPPLIED_BY":
            supplier_names.add(graph.nodes[supplier_id]["name"])

print("Suppliers:", sorted(supplier_names))