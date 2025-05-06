from typing import cast

from rdflib import Graph, Literal
from rdflib.query import ResultRow

import models as ontology



class OntologyIndexer:
    """
    OntologyIndexer is an utility class that provides methods to index the ontology
    """

    PREFIXES = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    """

    GET_CLASS_SPARQL = f"""
    {PREFIXES}

    SELECT DISTINCT ?class ?label ?description ?isDeprecated
    WHERE {{
        ?class a ?type .
        FILTER (?type = owl:Class || ?type = rdfs:Class)
        FILTER (!isBlank(?class))
        OPTIONAL {{ ?class rdfs:label ?label }}
        OPTIONAL {{ ?class rdfs:comment ?description }}
        OPTIONAL {{ ?class owl:deprecated ?isDeprecated }}
    }}
    """

    GET_SUPER_CLASSES_SPARQL = f"""
    {PREFIXES}
    SELECT DISTINCT ?superClass
    WHERE {{
        <___class_uri___> rdfs:subClassOf* ?superClass .
        FILTER (!isBlank(?superClass)) .
    }}
    """

    GET_PROPERTY_SPARQL = f"""
    {PREFIXES}
    SELECT DISTINCT ?property ?label ?description ?isDeprecated ?propertyType
    WHERE {{
        ?property a ?propertyType .
        FILTER (?propertyType = owl:ObjectProperty || ?propertyType = owl:DatatypeProperty || ?propertyType = owl:AnnotationProperty || ?propertyType = rdf:Property)
        FILTER (!isBlank(?property))
        OPTIONAL {{ ?property rdfs:label ?label }}
        OPTIONAL {{ ?property rdfs:comment ?description }}
        OPTIONAL {{ ?property owl:deprecated ?isDeprecated }}
    }}
    """

    GET_PROPERTY_RANGE_SPARQL = f"""
    {PREFIXES}
    SELECT DISTINCT ?range
    WHERE {{
        <___property_uri___> rdfs:range ?range .
        FILTER (!isBlank(?range)) .
    }}
    """

    GET_PROPERTY_RANGE_OWL_UNION_SPARQL = f"""
    {PREFIXES}
    SELECT DISTINCT ?range
    WHERE {{
        <___property_uri___> rdfs:range ?rangeValue .
        ?rangeValue owl:unionOf ?list .
        ?list rdf:rest*/rdf:first ?range .
        FILTER (!isBlank(?range)) .
    }}
    """

    GET_PROPERTY_RANGE_OWL_INTERSECTION_SPARQL = f"""
    {PREFIXES}
    SELECT DISTINCT ?range
    WHERE {{
        <___property_uri___> rdfs:range ?rangeValue .
        ?rangeValue owl:intersectionOf ?list .
        ?list rdf:rest*/rdf:first ?range .
        FILTER (!isBlank(?range)) .
    }}
    """

    GET_PROPERTY_DOMAIN_SPARQL = f"""
    {PREFIXES}

    SELECT DISTINCT ?domain
    WHERE {{
        <___property_uri___> rdfs:domain ?domain .
        FILTER (!isBlank(?domain)) .
    }}
    """

    GET_PROPERTY_DOMAIN_OWL_UNION_SPARQL = f"""
    {PREFIXES}
    SELECT DISTINCT ?domain
    WHERE {{
        <___property_uri___> rdfs:domain ?domainValue .
        ?domainValue owl:unionOf ?list .
        ?list rdf:rest*/rdf:first ?domain .
        FILTER (!isBlank(?domain)) .
    }}
    """

    GET_PROPERTY_DOMAIN_OWL_INTERSECTION_SPARQL = f"""
    {PREFIXES}
    SELECT DISTINCT ?domain
    WHERE {{
        <___property_uri___> rdfs:domain ?domainValue .
        ?domainValue owl:intersectionOf ?list .
        ?list rdf:rest*/rdf:first ?domain .
        FILTER (!isBlank(?domain)) .
    }}
    """

    GET_INDIVIDUAL_SPARQL = f"""
    {PREFIXES}
    SELECT DISTINCT ?individual ?label ?description ?isDeprecated
    WHERE {{
        ?individual a owl:NamedIndividual .
        FILTER (!isBlank(?individual))
        OPTIONAL {{ ?individual rdfs:label ?label }}
        OPTIONAL {{ ?individual rdfs:comment ?description }}
        OPTIONAL {{ ?individual owl:deprecated ?isDeprecated }}
    }}
    """

    def _create_literal_from_rdflib_literal(
        self, rdflib_literal: Literal
    ) -> ontology.Literal:
        return ontology.Literal(
            value=rdflib_literal.value,
            language=rdflib_literal.language or "en",
            datatype=rdflib_literal.datatype or "",
        )

    def get_classes(self, ontology_uri: str, g: Graph) -> list[ontology.Class]:
        """
        Get classes from the ontology

        Parameters:
            ontology_uri (str): The URI of the ontology
            g (Graph): The ontology graph

        Returns:
            list[models.Class]: The list of classes
        """
        classes_result = g.query(self.GET_CLASS_SPARQL)
        classes: dict[str, dict] = {}
        for class_result in classes_result:
            class_result = cast(ResultRow, class_result)
            class_uri = class_result["class"]
            if class_uri not in classes:
                classes[class_uri] = self._initialize_class_data(
                    g, class_uri, class_result
                )
            self._update_class_labels_and_descriptions(classes, class_uri, class_result)
        return self._create_class_models(ontology_uri, classes)

    def _initialize_class_data(
        self,
        g: Graph,
        class_uri: str,
        class_result: ResultRow,
    ) -> dict:
        super_classes_result = g.query(
            self.GET_SUPER_CLASSES_SPARQL.replace("___class_uri___", class_uri)
        )
        super_classes = [
            str(cast(ResultRow, super_class_result)["superClass"])
            for super_class_result in super_classes_result
        ]
        try:
            super_classes.remove(str(class_uri))
        except ValueError:
            pass
        is_deprecated = cast(Literal, class_result["isDeprecated"])
        return {
            "super_classes": super_classes,
            "label": [],
            "description": [],
            "is_deprecated": is_deprecated.toPython() if is_deprecated else False,
        }

    def _update_class_labels_and_descriptions(
        self,
        classes: dict,
        class_uri: str,
        class_result: ResultRow,
    ) -> None:
        result_label = cast(Literal, class_result["label"])
        result_description = cast(Literal, class_result["description"])
        if label := result_label:
            classes[class_uri]["label"].append(
                self._create_literal_from_rdflib_literal(label)
            )
        if description := result_description:
            classes[class_uri]["description"].append(
                self._create_literal_from_rdflib_literal(description)
            )

    def _create_class_models(
        self, ontology_uri: str, classes: dict
    ) -> list[ontology.Class]:
        return [
            ontology.Class(
                belongs_to=ontology_uri,
                full_uri=str(class_uri),
                label=class_data["label"],
                description=class_data["description"],
                super_classes=class_data["super_classes"],
                is_deprecated=class_data["is_deprecated"],
            )
            for class_uri, class_data in classes.items()
        ]

    def get_properties(self, ontology_uri: str, g: Graph) -> list[ontology.Property]:
        """
        Get properties from the ontology

        Parameters:
            ontology_uri (str): The URI of the ontology
            g (Graph): The ontology graph

        Returns:
            list[models.Property]: The list of properties
        """
        properties_result = g.query(self.GET_PROPERTY_SPARQL)
        properties: dict[str, dict] = {}
        for property_result in properties_result:
            property_result = cast(ResultRow, property_result)
            property_uri = property_result["property"]

            if property_uri not in properties:
                properties[property_uri] = self._initialize_property_data(
                    g, property_uri, property_result
                )

            self._update_property_labels_and_descriptions(
                properties, property_uri, property_result
            )

        return self._create_property_models(ontology_uri, properties)

    def _initialize_property_data(
        self,
        g: Graph,
        property_uri: str,
        property_result: ResultRow,
    ) -> dict:
        range_result = g.query(
            self.GET_PROPERTY_RANGE_SPARQL.replace("___property_uri___", property_uri)
        )
        range_union_result = g.query(
            self.GET_PROPERTY_RANGE_OWL_UNION_SPARQL.replace(
                "___property_uri___", property_uri
            )
        )
        range_intersection_result = g.query(
            self.GET_PROPERTY_RANGE_OWL_INTERSECTION_SPARQL.replace(
                "___property_uri___", property_uri
            )
        )
        range_values = [
            str(cast(ResultRow, range_row)["range"])
            for range_row in [
                *range_result,
                *range_union_result,
                *range_intersection_result,
            ]
        ]

        domain_result = g.query(
            self.GET_PROPERTY_DOMAIN_SPARQL.replace("___property_uri___", property_uri)
        )

        domain_union_result = g.query(
            self.GET_PROPERTY_DOMAIN_OWL_UNION_SPARQL.replace(
                "___property_uri___", property_uri
            )
        )

        domain_intersection_result = g.query(
            self.GET_PROPERTY_DOMAIN_OWL_INTERSECTION_SPARQL.replace(
                "___property_uri___", property_uri
            )
        )

        domain_values = [
            str(cast(ResultRow, domain_row)["domain"])
            for domain_row in [
                *domain_result,
                *domain_union_result,
                *domain_intersection_result,
            ]
        ]
        is_deprecated = cast(Literal, property_result["isDeprecated"])
        property_type = cast(ResultRow, property_result)["propertyType"]
        return {
            "label": [],
            "description": [],
            "property_type": self._get_property_type(str(property_type)),
            "range": range_values,
            "domain": domain_values,
            "is_deprecated": is_deprecated.toPython() if is_deprecated else False,
        }

    def _update_property_labels_and_descriptions(
        self,
        properties: dict,
        property_uri: str,
        property_result: ResultRow,
    ) -> None:
        if label := cast(Literal, property_result["label"]):
            properties[property_uri]["label"].append(
                self._create_literal_from_rdflib_literal(label)
            )
        if description := cast(Literal, property_result["description"]):
            properties[property_uri]["description"].append(
                self._create_literal_from_rdflib_literal(description)
            )

    def _create_property_models(
        self, ontology_uri: str, properties: dict
    ) -> list[ontology.Property]:
        return [
            ontology.Property(
                belongs_to=str(ontology_uri),
                full_uri=str(property_uri),
                label=property_data["label"],
                description=property_data["description"],
                property_type=property_data["property_type"],
                range=property_data["range"],
                domain=property_data["domain"],
                is_deprecated=property_data["is_deprecated"],
            )
            for property_uri, property_data in properties.items()
        ]

    def _get_property_type(self, property_type: str) -> ontology.PropertyType:
        match property_type:
            case "http://www.w3.org/2002/07/owl#ObjectProperty":
                return ontology.PropertyType.OBJECT
            case "http://www.w3.org/2002/07/owl#DatatypeProperty":
                return ontology.PropertyType.DATATYPE
            case "http://www.w3.org/2002/07/owl#AnnotationProperty":
                return ontology.PropertyType.ANNOTATION
            case _:
                raise ValueError(f"Unknown property type: {property_type}")

    def get_individuals(self, ontology_uri: str, g: Graph) -> list[ontology.Individual]:
        """
        Get individuals from the ontology

        Parameters:
            ontology_uri (str): The URI of the ontology
            g (Graph): The ontology graph

        Returns:
            list[models.Individual]: The list of individuals
        """
        individuals_result = g.query(self.GET_INDIVIDUAL_SPARQL)
        individuals: dict[str, dict] = {}
        for individual_result in individuals_result:
            individual_result = cast(ResultRow, individual_result)
            individual_uri = individual_result["individual"]

            if individual_uri not in individuals:
                individuals[individual_uri] = {
                    "label": [],
                    "description": [],
                    "is_deprecated": False,
                }

            self._update_individual_labels_and_descriptions(
                individuals,
                individual_uri,
                individual_result,
            )

        return self._create_individual_models(ontology_uri, individuals)

    def _update_individual_labels_and_descriptions(
        self,
        individuals: dict,
        individual_uri: str,
        individual_result: ResultRow,
    ) -> None:
        result_label = cast(Literal, individual_result["label"])
        result_description = cast(Literal, individual_result["description"])
        is_deprecated = cast(Literal, individual_result["isDeprecated"])

        if result_label:
            individuals[individual_uri]["label"].append(
                self._create_literal_from_rdflib_literal(result_label)
            )
        if result_description:
            individuals[individual_uri]["description"].append(
                self._create_literal_from_rdflib_literal(result_description)
            )
        if is_deprecated:
            individuals[individual_uri]["is_deprecated"] = is_deprecated.toPython()

    def _create_individual_models(
        self, ontology_uri: str, individuals: dict
    ) -> list[ontology.Individual]:
        return [
            ontology.Individual(
                belongs_to=ontology_uri,
                full_uri=str(individual_uri),
                label=individual_data["label"],
                description=individual_data["description"],
                is_deprecated=individual_data["is_deprecated"],
            )
            for individual_uri, individual_data in individuals.items()
        ]