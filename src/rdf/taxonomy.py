# 04_taxonomy.py
import networkx as nx

taxonomy = nx.DiGraph()

# Specific category -> broader category
taxonomy.add_edges_from([
    ("Laptop", "Computer"),
    ("Desktop", "Computer"),
    ("Computer", "Electronics"),
    ("Smartphone", "Electronics"),
    ("Electronics", "Product"),
    ("Furniture", "Product"),
    ("Chair", "Furniture"),
])

# A taxonomy in this example must have no cycles.
if not nx.is_directed_acyclic_graph(taxonomy):
    raise ValueError("The taxonomy contains a cycle.")

products = {
    "Laptop X": "Laptop",
    "Phone Y": "Smartphone",
    "Office Chair": "Chair",
}

def belongs_to(category: str, broader_category: str) -> bool:
    return (
        category == broader_category
        or nx.has_path(taxonomy, category, broader_category)
    )

# Because edges point toward broader categories,
# descendants() returns reachable broader categories.
print(
    "Broader categories of Laptop:",
    sorted(nx.descendants(taxonomy, "Laptop")),
)

# Query: find every product classified under Electronics.
print("\nElectronic products:")

for product_name, category in products.items():
    if belongs_to(category, "Electronics"):
        print(product_name)