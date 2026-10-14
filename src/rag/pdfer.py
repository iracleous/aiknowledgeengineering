"""
uv add pypdf
simple pdf extraction example

"""


from pypdf import PdfReader

reader = PdfReader(f"pdfs\CELEX_32016R0679_EL_TXT.pdf")

# for number, page in enumerate(reader.pages, start=1):
#     print(f"\n--- Page {number} ---")
#     print(page.extract_text() or "")

text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
print(text)
print(len(text))
print("-" * 80)

import re

chunks = re.split(r"(?=^[ \t]*\(\d+\))", text, flags=re.MULTILINE)
chunks = [chunk.strip() for chunk in chunks if chunk.strip()]

for i, chunk in enumerate(chunks):
    print(f"\n--- Chunk {i + 1} ---")
    print(chunk)
    if i==50: break

