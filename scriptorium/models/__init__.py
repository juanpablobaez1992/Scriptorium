"""
models/__init__.py
Registro central de modelos SQLAlchemy.
Arquitectura: Models package.
"""

from scriptorium.models.category import Category
from scriptorium.models.classification_log import ClassificationLog
from scriptorium.models.idea import IDEA_STATUSES, INPUT_TYPES, MATURITY_LEVELS, Idea
from scriptorium.models.input_file import InputFile
from scriptorium.models.project import Project
from scriptorium.models.relation import RELATION_TYPES, Relation
from scriptorium.models.review import Review
from scriptorium.models.scope import Scope
from scriptorium.models.tag import Tag, idea_tags
from scriptorium.models.task import Task
from scriptorium.models.taxonomy_suggestion import TaxonomySuggestion

__all__ = [
    "Category",
    "ClassificationLog",
    "IDEA_STATUSES",
    "INPUT_TYPES",
    "MATURITY_LEVELS",
    "Idea",
    "InputFile",
    "Project",
    "RELATION_TYPES",
    "Relation",
    "Review",
    "Scope",
    "Tag",
    "Task",
    "TaxonomySuggestion",
    "idea_tags",
]
