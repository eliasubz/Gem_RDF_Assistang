# Matching columns and paths

In order to get a colum-to-path-matching we run:
python '.\Experiment 2\schema_creation_prompting.py'

To evaluate the evaluation folders we run:
python '.\Experiment 2\schema_eval.py'

To evaluate multiple evaluations we run:
python '.\Experiment 2\meta_eval.py'

The llm_to_rdfCraft notebook contains logic to convert column-to-path-matchings into rdf_craft logic.