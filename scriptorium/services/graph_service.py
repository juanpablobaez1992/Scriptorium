"""
services/graph_service.py
Construccion de datos de grafo para Cytoscape.js.
Arquitectura: Services.
"""

from __future__ import annotations

from scriptorium.models import Idea, Relation


class GraphService:
    """Construye nodos y aristas para vista tipo Obsidian."""

    def build_graph(self, filters: dict | None = None) -> dict:
        filters = filters or {}
        query = Idea.query.filter(Idea.is_archived.is_(False))
        if filters.get("scope_id"):
            query = query.filter_by(scope_id=filters["scope_id"])
        if filters.get("project_id"):
            query = query.filter_by(project_id=filters["project_id"])
        if filters.get("category_id"):
            query = query.filter_by(category_id=filters["category_id"])
        if filters.get("status"):
            query = query.filter_by(status=filters["status"])

        ideas = query.all()
        idea_ids = [idea.id for idea in ideas]
        edges = []
        nodes = []

        for idea in ideas:
            rc = idea.relation_count()
            is_core = rc >= 5
            if filters.get("orphan_only") and rc > 0:
                continue
            if filters.get("core_only") and not is_core:
                continue
            nodes.append(
                {
                    "data": {
                        "id": f"idea-{idea.id}",
                        "label": idea.title,
                        "type": "idea",
                        "category": idea.category.name if idea.category else "",
                        "scope": idea.scope.name if idea.scope else "",
                        "project": idea.project.name if idea.project else "",
                        "status": idea.status,
                        "size": self._node_size(idea),
                    }
                }
            )
            if idea.scope:
                nodes.append(
                    {
                        "data": {
                            "id": f"scope-{idea.scope.id}",
                            "label": idea.scope.name,
                            "type": "scope",
                            "size": 24,
                        }
                    }
                )
                edges.append(
                    {
                        "data": {
                            "source": f"scope-{idea.scope.id}",
                            "target": f"idea-{idea.id}",
                            "label": "contiene",
                            "weight": 0.4,
                        }
                    }
                )
            if idea.project:
                nodes.append(
                    {
                        "data": {
                            "id": f"project-{idea.project.id}",
                            "label": idea.project.name,
                            "type": "project",
                            "size": 22,
                        }
                    }
                )
                edges.append(
                    {
                        "data": {
                            "source": f"project-{idea.project.id}",
                            "target": f"idea-{idea.id}",
                            "label": "estructura",
                            "weight": 0.45,
                        }
                    }
                )
            if idea.category:
                nodes.append(
                    {
                        "data": {
                            "id": f"category-{idea.category.id}",
                            "label": idea.category.name,
                            "type": "category",
                            "size": 20,
                        }
                    }
                )
                edges.append(
                    {
                        "data": {
                            "source": f"category-{idea.category.id}",
                            "target": f"idea-{idea.id}",
                            "label": "clasifica",
                            "weight": 0.38,
                        }
                    }
                )
            for tag in idea.tags[:4]:
                nodes.append(
                    {
                        "data": {
                            "id": f"tag-{tag.id}",
                            "label": tag.name,
                            "type": "tag",
                            "size": 16,
                        }
                    }
                )
                edges.append(
                    {
                        "data": {
                            "source": f"tag-{tag.id}",
                            "target": f"idea-{idea.id}",
                            "label": "etiqueta",
                            "weight": 0.3,
                        }
                    }
                )

        min_strength = float(filters.get("min_strength", 0) or 0)
        relations = (
            Relation.query.filter(Relation.source_idea_id.in_(idea_ids)).all()
            if idea_ids
            else []
        )
        for rel in relations:
            if rel.target_idea_id not in idea_ids or rel.strength < min_strength:
                continue
            edges.append(
                {
                    "data": {
                        "source": f"idea-{rel.source_idea_id}",
                        "target": f"idea-{rel.target_idea_id}",
                        "label": rel.relation_type,
                        "weight": rel.strength,
                    }
                }
            )

        return {"nodes": self._unique_nodes(nodes), "edges": edges}

    def _node_size(self, idea: Idea) -> int:
        size = 24 + (idea.relation_count() * 2)
        if idea.priority >= 4:
            size += 4
        if idea.project and idea.project.status == "activo":
            size += 3
        return min(60, size)

    def _unique_nodes(self, nodes: list[dict]) -> list[dict]:
        seen = set()
        unique = []
        for node in nodes:
            node_id = node["data"]["id"]
            if node_id in seen:
                continue
            seen.add(node_id)
            unique.append(node)
        return unique
