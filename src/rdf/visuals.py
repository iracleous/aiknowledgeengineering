"""
06 visuals.py
uv add networkx matplotlib

"""

import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

OUTPUT = Path("graph_visuals")
OUTPUT.mkdir(exist_ok=True)

# Colors distinguish instances, classes, and literal values.
INSTANCE = "#BFDBFE"
CLASS = "#BBF7D0"
LITERAL = "#FDE68A"


def draw_graph(ax, graph, positions, title, note):
    """Draw a small, directed, labeled graph."""
    node_size = 3200

    nx.draw_networkx_nodes(
        graph,
        positions,
        ax=ax,
        node_size=node_size,
        node_color=[
            graph.nodes[node].get("color", INSTANCE)
            for node in graph.nodes
        ],
        edgecolors="#334155",
    )

    nx.draw_networkx_labels(
        graph,
        positions,
        ax=ax,
        labels={
            node: graph.nodes[node].get("text", node)
            for node in graph.nodes
        },
        font_size=9,
    )

    nx.draw_networkx_edges(
        graph,
        positions,
        ax=ax,
        node_size=node_size,
        arrows=True,
        arrowsize=20,
        edge_color="#64748B",
        width=1.6,
    )

    nx.draw_networkx_edge_labels(
        graph,
        positions,
        ax=ax,
        edge_labels=nx.get_edge_attributes(graph, "text"),
        font_size=8,
        rotate=False,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.9},
    )

    ax.set_title(title, fontsize=14, fontweight="bold", pad=18)
    ax.text(
        0.5, -0.08, note,
        transform=ax.transAxes,
        ha="center",
        fontsize=10,
    )
    ax.margins(0.30)
    ax.axis("off")


fig, axes = plt.subplots(3, 2, figsize=(18, 18))
fig.suptitle(
    "Knowledge Graph Foundations",
    fontsize=22,
    fontweight="bold",
)

# -------------------------------------------------
# 1. ENTITIES
# -------------------------------------------------
entities = nx.DiGraph()

entities.add_node(
    "alice",
    text="Alice\nCustomer\nregion: Athens",
)
entities.add_node(
    "laptop",
    text="Laptop X\nProduct\nprice: 1200 EUR",
)
entities.add_node(
    "supplier",
    text="TechSupply\nSupplier",
)

draw_graph(
    axes[0, 0],
    entities,
    {
        "alice": (0, 1),
        "laptop": (1, 1),
        "supplier": (0.5, 0),
    },
    "1. Entities",
    "Each node represents an identifiable object.",
)

# -------------------------------------------------
# 2. RELATIONSHIPS
# -------------------------------------------------
relationships = nx.DiGraph()

relationships.add_node("alice", text="Alice\nCustomer")
relationships.add_node("laptop", text="Laptop X\nProduct")
relationships.add_node("supplier", text="TechSupply\nSupplier")

relationships.add_edge("alice", "laptop", text="PURCHASED")
relationships.add_edge("laptop", "supplier", text="SUPPLIED_BY")

draw_graph(
    axes[0, 1],
    relationships,
    {
        "alice": (0, 1),
        "laptop": (1, 0.5),
        "supplier": (0, 0),
    },
    "2. Relationships",
    "Arrows connect entities and describe their relationship.",
)

# -------------------------------------------------
# 3. ONTOLOGY
# This panel shows schema definitions, not instances.
# -------------------------------------------------
ontology = nx.DiGraph()

ontology.add_node("person", text="Person\nClass", color=CLASS)
ontology.add_node("customer", text="Customer\nClass", color=CLASS)
ontology.add_node("product", text="Product\nClass", color=CLASS)
ontology.add_node(
    "purchases",
    text="purchases\nProperty",
    color=LITERAL,
)

ontology.add_edge("customer", "person", text="subClassOf")
ontology.add_edge("purchases", "customer", text="domain")
ontology.add_edge("purchases", "product", text="range")

draw_graph(
    axes[1, 0],
    ontology,
    {
        "person": (0, 1.5),
        "customer": (0, 0.5),
        "purchases": (1, 0),
        "product": (2, 0.5),
    },
    "3. Ontology",
    "Defines classes and the meaning of a property.",
)

# -------------------------------------------------
# 4. TAXONOMY
# Arrows point from specific to broader categories.
# -------------------------------------------------
taxonomy = nx.DiGraph()

for category in [
    "Product", "Electronics", "Furniture",
    "Computer", "Smartphone", "Chair", "Laptop",
]:
    taxonomy.add_node(category, color=CLASS)

for specific, broader in [
    ("Electronics", "Product"),
    ("Furniture", "Product"),
    ("Computer", "Electronics"),
    ("Smartphone", "Electronics"),
    ("Chair", "Furniture"),
    ("Laptop", "Computer"),
]:
    taxonomy.add_edge(specific, broader, text="is a")

draw_graph(
    axes[1, 1],
    taxonomy,
    {
        "Product": (0, 3),
        "Electronics": (-0.8, 2),
        "Furniture": (1, 2),
        "Computer": (-1.3, 1),
        "Smartphone": (0, 1),
        "Chair": (1, 1),
        "Laptop": (-1.3, 0),
    },
    "4. Taxonomy",
    "Specific categories point toward broader categories.",
)

# -------------------------------------------------
# 5. RDF
# Purchase metadata is represented using an entity.
# Literal values are yellow nodes.
# -------------------------------------------------
rdf = nx.DiGraph()

rdf.add_node("purchase", text="ex:Purchase001")
rdf.add_node("alice", text="ex:Alice")
rdf.add_node("laptop", text="ex:LaptopX")
rdf.add_node("quantity", text="2\nInteger literal", color=LITERAL)
rdf.add_node(
    "date",
    text="2026-10-01\nDate literal",
    color=LITERAL,
)

rdf.add_edge("purchase", "alice", text="ex:customer")
rdf.add_edge("purchase", "laptop", text="ex:product")
rdf.add_edge("purchase", "quantity", text="ex:quantity")
rdf.add_edge("purchase", "date", text="ex:date")

draw_graph(
    axes[2, 0],
    rdf,
    {
        "purchase": (0, 0),
        "alice": (-1, 1),
        "laptop": (1, 1),
        "quantity": (-1, -1),
        "date": (1, -1),
    },
    "5. RDF: Purchase as an Entity",
    "Each arrow represents a subject-predicate-object triple.",
)

# -------------------------------------------------
# 6. PROPERTY GRAPH
# Purchase metadata is stored on the relationship.
# -------------------------------------------------
property_graph = nx.DiGraph()

property_graph.add_node(
    "alice",
    text="Customer\nname: Alice",
)
property_graph.add_node(
    "laptop",
    text="Product\nname: Laptop X",
)

property_graph.add_edge(
    "alice",
    "laptop",
    text="PURCHASED\nquantity: 2\ndate: 2026-10-01",
)

draw_graph(
    axes[2, 1],
    property_graph,
    {
        "alice": (0, 0),
        "laptop": (2, 0),
    },
    "6. Property Graph",
    "Nodes and relationships can carry properties.",
)

fig.tight_layout(rect=(0, 0.02, 1, 0.96), h_pad=5, w_pad=3)

# Save before opening the display window.
png_path = OUTPUT / "knowledge_graph_foundations.png"
pdf_path = OUTPUT / "knowledge_graph_foundations.pdf"

fig.savefig(png_path, dpi=200, bbox_inches="tight")
fig.savefig(pdf_path, bbox_inches="tight")

print(f"PNG saved to: {png_path.resolve()}")
print(f"PDF saved to: {pdf_path.resolve()}")

plt.show()