# from dataclasses import dataclass
# from enum import StrEnum

# class OntologyPropertyType(StrEnum):
#     """
#     Represents the type of an ontology property.
#     """
#     OBJECT_PROPERTY = "ObjectProperty"
#     DATA_PROPERTY = "DataProperty"


# @dataclass
# class OntologyProperty:
#     type: OntologyPropertyType
#     full_uri: str

#     def to_dict(self):
#         """
#         Converts the OntologyProperty instance to a dictionary.
#         """
#         return {
#             "type": self.type,
#             "full_uri": self.full_uri
#         }


# @dataclass
# class OntologyClass:
#     """
#     Represents an ontology class with a name and a list of properties.
#     """
#     name: str
#     full_uri: str
#     domain: list[OntologyProperty]
#     range: list[OntologyProperty]

#     def to_dict(self):
#         """
#         Converts the OntologyClass instance to a dictionary.
#         """
#         return {
#             "name": self.name,
#             "full_uri": self.full_uri,
#             "domain": [prop.to_dict() for prop in self.domain],
#             "range": [prop.to_dict() for prop in self.range]
#         }



from dataclasses import dataclass, field
from enum import StrEnum


@dataclass(kw_only=True)
class Literal:
    """
    A literal is a value that is not a URI, but a string, integer, etc.

    Attributes:
        value (str): The value of the literal
        datatype (str): The datatype of the literal
        language (str): The language of the literal
    """

    value: str
    datatype: str = ""
    language: str = ""

    def to_dict(self):
        return {
            "value": self.value,
            "datatype": self.datatype,
            "language": self.language,
        }

    @classmethod
    def from_dict(cls, data):
        if "value" not in data:
            raise ValueError("value is required")
        if "datatype" not in data:
            data["datatype"] = ""
        if "language" not in data:
            data["language"] = ""
        return cls(
            value=data["value"],
            datatype=data["datatype"],
            language=data["language"],
        )


class NamedNodeType(StrEnum):
    """
    Enumeration of the types of named nodes.
    """

    CLASS = "class"
    INDIVIDUAL = "individual"
    PROPERTY = "property"


class PropertyType(StrEnum):
    """
    Enumeration of the types of properties.
    """

    OBJECT = "object"
    DATATYPE = "datatype"
    ANNOTATION = "annotation"
    ANY = "any"


@dataclass(kw_only=True)
class NamedNode:
    """
    A named node is a node that has a URI.

    Attributes:
        belongs_to (str): The URI of the ontology that the node belongs to
        full_uri (str): The full URI of the node
        label (list[Literal]): The label of the node
        description (list[Literal]): The description of the node
        is_deprecated (bool): Whether the node is deprecated
    """

    belongs_to: str
    type: NamedNodeType
    full_uri: str
    label: list[Literal]
    description: list[Literal]
    is_deprecated: bool

    def to_dict(self):
        return {
            "belongs_to": self.belongs_to,
            "type": self.type,
            "full_uri": self.full_uri,
            "label": [label.to_dict() for label in self.label],
            "description": [desc.to_dict() for desc in self.description],
            "is_deprecated": self.is_deprecated,
        }

    @classmethod
    def from_dict(cls, data):
        if "belongs_to" not in data:
            raise ValueError("belongs_to is required")
        if "type" not in data:
            raise ValueError("type is required")
        if "full_uri" not in data:
            raise ValueError("full_uri is required")
        if "label" not in data:
            raise ValueError("label is required")
        if "description" not in data:
            raise ValueError("description is required")
        if "is_deprecated" not in data:
            data["is_deprecated"] = False
        return cls(
            belongs_to=data["belongs_to"],
            type=data["type"],
            full_uri=data["full_uri"],
            label=[Literal.from_dict(label) for label in data["label"]],
            description=[Literal.from_dict(desc) for desc in data["description"]],
            is_deprecated=data["is_deprecated"],
        )


@dataclass(kw_only=True)
class Individual(NamedNode):
    """
    An individual is a named node that is an instance of a class.

    Inherits from NamedNode.
    """

    type: NamedNodeType = field(default=NamedNodeType.INDIVIDUAL)

    def __post_init__(self):
        if self.type != NamedNodeType.INDIVIDUAL:
            raise ValueError(f"Individual must have type {NamedNodeType.INDIVIDUAL}")

    def to_dict(self):
        return {
            **super().to_dict(),
            "type": self.type,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            belongs_to=data["belongs_to"],
            type=data["type"],
            full_uri=data["full_uri"],
            label=[Literal.from_dict(label) for label in data["label"]],
            description=[Literal.from_dict(desc) for desc in data["description"]],
            is_deprecated=data["is_deprecated"],
        )


@dataclass(kw_only=True)
class Class(NamedNode):
    """
    A class is a named node that is a class.

    Inherits from NamedNode.

    Attributes:
        super_classes (list[str]): Full URIs of the super classes of the class
    """

    super_classes: list[str]
    type: NamedNodeType = NamedNodeType.CLASS

    def __post_init__(self):
        if self.type != NamedNodeType.CLASS:
            raise ValueError(f"Class must have type {NamedNodeType.CLASS}")

    def to_dict(self):
        return {
            **super().to_dict(),
            "super_classes": self.super_classes,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            belongs_to=data["belongs_to"],
            type=data["type"],
            full_uri=data["full_uri"],
            label=[Literal.from_dict(label) for label in data["label"]],
            description=[Literal.from_dict(desc) for desc in data["description"]],
            is_deprecated=data["is_deprecated"],
            super_classes=data["super_classes"],
        )


@dataclass(kw_only=True)
class Property(NamedNode):
    """
    A property is a named node that is a property.

    Inherits from NamedNode.

    Attributes:
        property_type (PropertyType): The type of the property
        range (list[str]): Full URIs of the range of the property. Either a class or a datatype
        domain (list[str]): Full URIs of the domain of the property. Either a class or an individual
    """

    property_type: PropertyType
    range: list[str]
    domain: list[str]
    type: NamedNodeType = NamedNodeType.PROPERTY

    def __post_init__(self):
        if self.type != NamedNodeType.PROPERTY:
            raise ValueError(f"Property must have type {NamedNodeType.PROPERTY}")

    def to_dict(self):
        return {
            **super().to_dict(),
            "property_type": self.property_type,
            "range": self.range,
            "domain": self.domain,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            belongs_to=data["belongs_to"],
            type=data["type"],
            full_uri=data["full_uri"],
            label=[Literal.from_dict(label) for label in data["label"]],
            description=[Literal.from_dict(desc) for desc in data["description"]],
            is_deprecated=data["is_deprecated"],
            property_type=data["property_type"],
            range=data["range"],
            domain=data["domain"],
        )


@dataclass(kw_only=True)
class Ontology:
    """
    An ontology is a collection of named nodes.

    Attributes:
        uuid (str): The UUID of the ontology
        file_uuid (str): The UUID of the file that the ontology is in
        name (str): The name of the ontology
        description (str): The description of the ontology
        base_uri (str): The base URI of the ontology
        classes (list[Class]): The classes in the ontology
        individuals (list[Individual]): The individuals in the ontology
        properties (list[Property]): The properties in the ontology

    """

    uuid: str
    file_uuid: str
    name: str
    description: str
    base_uri: str
    classes: list[Class]
    individuals: list[Individual]
    properties: list[Property]

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "file_uuid": self.file_uuid,
            "name": self.name,
            "description": self.description,
            "base_uri": self.base_uri,
            "classes": [cls.to_dict() for cls in self.classes],
            "individuals": [ind.to_dict() for ind in self.individuals],
            "properties": [prop.to_dict() for prop in self.properties],
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            uuid=data["uuid"],
            file_uuid=data["file_uuid"],
            name=data["name"],
            description=data["description"],
            base_uri=data["base_uri"],
            classes=[Class.from_dict(cls) for cls in data["classes"]],
            individuals=[Individual.from_dict(ind) for ind in data["individuals"]],
            properties=[Property.from_dict(prop) for prop in data["properties"]],
        )