"""
# 03_ontology.py
RDF represents facts as subject–predicate–object triples.
Here, we model the purchase as an entity so it can
 have quantity and date attributes.
"""



from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS
from owlrl import DeductiveClosure, RDFS_Semantics




EX = Namespace("https://example.org/")

graph = Graph()
graph.bind("ex", EX)

# Define classes.
graph.add((EX.Person, RDF.type, RDFS.Class))
graph.add((EX.Customer, RDF.type, RDFS.Class))
graph.add((EX.Product, RDF.type, RDFS.Class))

# Every Customer is also a Person.
graph.add((EX.Customer, RDFS.subClassOf, EX.Person))

# Define a relationship and its meaning.
graph.add((EX.purchases, RDF.type, RDF.Property))
graph.add((EX.purchases, RDFS.domain, EX.Customer))
graph.add((EX.purchases, RDFS.range, EX.Product))

# Business fact. No explicit types are assigned to these entities.
graph.add((EX.Alice, EX.purchases, EX.LaptopX))

print(
    "Before reasoning: Alice is a Person:",
    (EX.Alice, RDF.type, EX.Person) in graph,
)

# Materialize facts implied by the ontology.
DeductiveClosure(RDFS_Semantics).expand(graph)

print(
    "After reasoning: Alice is a Customer:",
    (EX.Alice, RDF.type, EX.Customer) in graph,
)

print(
    "After reasoning: Alice is a Person:",
    (EX.Alice, RDF.type, EX.Person) in graph,
)

print(
    "After reasoning: LaptopX is a Product:",
    (EX.LaptopX, RDF.type, EX.Product) in graph,
)