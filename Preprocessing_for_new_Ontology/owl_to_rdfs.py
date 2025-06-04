import re

# Preprocessing for ontology
# This script breaks up OWL strucutres in ontologies


def flatten_union_axioms(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern to match rdfs:range or rdfs:domain with owl:unionOf
    pattern = re.compile(
        r"(rdfs:(?:range|domain))\s+\[\s*rdf:type\s+owl:Class\s*;\s*owl:unionOf\s+\(([^)]+)\)\s*\]",
        re.MULTILINE,
    )

    def replacer(match):
        prop = match.group(1)
        classes = match.group(2).strip().split()
        return "\n".join(
            f"                                                                  {prop} {cls} ;"
            for cls in classes
        )

    new_content = pattern.sub(replacer, content)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(new_content)


# Example usage:
flatten_union_axioms("aidava-sphn.ttl", "aidava-sphn-flat.ttl")
