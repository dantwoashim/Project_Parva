"""Trust algebra primitives for proof-carrying temporal claims."""

from .field_provenance import FieldProvenance, ProvenanceMap
from .taint import AuthorityTaint, TaintedValue, TaintFlag, authority_join
from .upgrade import ReviewWitness, apply_review_upgrade

__all__ = [
    "AuthorityTaint",
    "FieldProvenance",
    "ProvenanceMap",
    "ReviewWitness",
    "TaintFlag",
    "TaintedValue",
    "apply_review_upgrade",
    "authority_join",
]
