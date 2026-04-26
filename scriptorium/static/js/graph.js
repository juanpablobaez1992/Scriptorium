/*
static/js/graph.js
Renderiza el grafo interactivo con Cytoscape.js.
Arquitectura: Views/Frontend JS.
*/

async function loadGraph() {
  const params = new URLSearchParams();
  const scope = document.getElementById("scopeFilter")?.value;
  const project = document.getElementById("projectFilter")?.value;
  const category = document.getElementById("categoryFilter")?.value;
  const minStrength = document.getElementById("minStrength")?.value;
  const coreOnly = document.getElementById("coreOnly")?.checked;
  if (scope) params.append("scope_id", scope);
  if (project) params.append("project_id", project);
  if (category) params.append("category_id", category);
  if (minStrength) params.append("min_strength", minStrength);
  if (coreOnly) params.append("core_only", "1");

  const res = await fetch(`/api/graph?${params.toString()}`);
  const data = await res.json();
  renderGraph(data);
}

function nodeColor(type) {
  if (type === "idea") return "#3b82f6"; // Blue 500
  if (type === "scope") return "#8b5cf6"; // Violet 500
  if (type === "project") return "#0ea5e9";
  if (type === "category") return "#10b981"; // Emerald 500
  if (type === "tag") return "#64748b";
  return "#9ca3af";
}

function renderGraph(data) {
  const container = document.getElementById("graphContainer");
  if (!container) return;
  const cy = cytoscape({
    container,
    elements: [...(data.nodes || []), ...(data.edges || [])],
    style: [
      {
        selector: "node",
        style: {
          "background-color": (ele) => nodeColor(ele.data("type")),
          label: "data(label)",
          color: "#ffffff",
          "font-size": 11,
          "font-weight": "bold",
          "text-valign": "center",
          "text-halign": "center",
          "text-outline-width": 1.5,
          "text-outline-color": (ele) => nodeColor(ele.data("type")),
          width: "data(size)",
          height: "data(size)",
          "text-wrap": "wrap",
          "text-max-width": 90,
          "border-width": 2,
          "border-color": "#ffffff",
          "border-opacity": 0.9,
          "transition-property": "width, height, border-width, border-color",
          "transition-duration": "0.2s"
        },
      },
      {
        selector: "node:selected",
        style: {
          "border-color": "#fbbf24",
          "border-width": 4,
          "width": "calc(data(size) + 10)",
          "height": "calc(data(size) + 10)",
        }
      },
      {
        selector: "edge",
        style: {
          width: (ele) => 1 + (ele.data("weight") || 0) * 3,
          "line-color": "#cbd5e1",
          "target-arrow-color": "#cbd5e1",
          "target-arrow-shape": "triangle",
          "curve-style": "bezier",
          label: "data(label)",
          "font-size": 9,
          "text-background-opacity": 0.8,
          "text-background-color": "#ffffff",
          "text-background-padding": 2,
          "text-background-shape": "roundrectangle",
        },
      },
    ],
    layout: { name: "cose", animate: true, fit: true, padding: 25 },
  });

  cy.on("tap", "node", (evt) => {
    const id = evt.target.id();
    if (id.startsWith("idea-")) {
      const ideaId = id.replace("idea-", "");
      window.location.href = `/ideas/${ideaId}`;
    }
  });
}

document.getElementById("reloadGraph")?.addEventListener("click", loadGraph);
window.addEventListener("DOMContentLoaded", loadGraph);
