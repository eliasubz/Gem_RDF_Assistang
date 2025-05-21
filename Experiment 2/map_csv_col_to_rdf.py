import os
import pandas as pd
from rdflib import Graph, Literal


def map_csv_to_rdf(csv_path, ttl_path, output_folder):
    # Load RDF TTL file
    g = Graph()
    g.parse(ttl_path, format="ttl")

    # Load CSV
    df = pd.read_csv(csv_path)

    column_mappings = {}

    # Generate output filename
    ttl_filename = os.path.splitext(os.path.basename(ttl_path))[0]
    output_file_path = os.path.join(output_folder, f"{ttl_filename}_parsed.txt")

    with open(output_file_path, "w", encoding="utf-8") as f_out:
        for column in df.columns:
            values = df[column].dropna().astype(str).unique()
            matched = set()

            for value in values:
                lit = Literal(value)
                for s, p, o in g.triples((None, None, lit)):
                    matched.add((str(p), str(s)))

            # Write section header
            f_out.write(f"Column: {column}\n")

            if matched:
                for predicate, subject in matched:
                    f_out.write(
                        f"  ↳ RDF Predicate: {predicate} (Subject: {subject})\n"
                    )
            else:
                f_out.write("  ↳ No match found in RDF\n")

            f_out.write("\n")  # Blank line between columns

    print(f"✅ Output saved to: {output_file_path}")
    return output_file_path


# Example usage
if __name__ == "__main__":
    csv_path = "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/UM/BC/csv/table-FOLLOW-UP-csv.csv"  # replace with your CSV path
    ttl_path = "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/UM/BC/rdf/FOLLOWUP_UM_RDF.txt"
    target_path = (
        "C:/Users/elias/Documents/ANI/Bachelor_Baby/llm_assistant/UM/BC/target"
    )

    map_csv_to_rdf(csv_path, ttl_path, target_path)
