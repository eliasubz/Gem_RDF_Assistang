from pydantic import BaseModel
from typing import List


class Entity(BaseModel):
    """Represents an entity with its label, IRI, and description."""

    label: str
    iri: str
    description: str

    class Config:
        frozen = True  # makes it immutable and hashable


class SpanningEntityOutput(BaseModel):
    """Represents the output containing a list of spanning entity candidates."""

    spanning_entity_candidates: List[Entity]
