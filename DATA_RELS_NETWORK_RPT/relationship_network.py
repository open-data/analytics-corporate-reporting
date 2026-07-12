#!/usr/bin/env python3

import argparse
import csv
import gzip
import html
import io
import json
import os
import re
import tempfile
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_SOURCE = "https://open.canada.ca/static/od-do-canada.jsonl.gz"
DEFAULT_CHART_DIR = "DATA_RELS_NETWORK_RPT/charts"
DEFAULT_STATS_CSV = "DATA_RELS_NETWORK_RPT/relationship_network_stats.csv"
DEFAULT_OVERVIEW_PNG = "DATA_RELS_NETWORK_RPT/network_overview.png"
DEFAULT_README = "DATA_RELS_NETWORK_RPT/README.md"
REQUEST_TIMEOUT_SECONDS = int(os.environ.get("REQUEST_TIMEOUT_SECONDS", "90"))
README_REPORT_START = "<!-- RELATIONSHIP_NETWORK_REPORT_START -->"
README_REPORT_END = "<!-- RELATIONSHIP_NETWORK_REPORT_END -->"

OPEN_CANADA_ID_RE = re.compile(
    r"/(?:dataset|info)/([0-9a-fA-F-]{36})(?:/resource/([0-9a-fA-F-]{36}))?"
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate department relationship network Mermaid charts and metrics."
    )
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="JSONL or JSONL.GZ source path/URL.")
    parser.add_argument("--chart-dir", default=DEFAULT_CHART_DIR, help="Directory for department chart markdown files.")
    parser.add_argument("--stats-csv", default=DEFAULT_STATS_CSV, help="Daily department metrics CSV path.")
    parser.add_argument("--overview-png", default=DEFAULT_OVERVIEW_PNG, help="Path for the overall network PNG.")
    parser.add_argument("--readme", default=DEFAULT_README, help="README path to update with generated report summary.")
    parser.add_argument("--date", default=None, help="Override run date in YYYY-MM-DD format.")
    parser.add_argument("--limit", type=int, default=None, help="Optional package limit for smoke tests.")
    parser.add_argument(
        "--skip-overview-image",
        action="store_true",
        help="Do not generate the overall network PNG.",
    )
    parser.add_argument(
        "--skip-readme",
        action="store_true",
        help="Do not update the generated README summary.",
    )
    parser.add_argument(
        "--no-stats",
        action="store_true",
        help="Generate charts only and do not update the stats CSV.",
    )
    return parser.parse_args()


def open_jsonl_source(source):
    if source.startswith(("http://", "https://")):
        response = urllib.request.urlopen(source, timeout=REQUEST_TIMEOUT_SECONDS)
        if source.endswith(".gz"):
            return gzip.open(response, mode="rt", encoding="utf-8")
        return io.TextIOWrapper(response, encoding="utf-8")

    if source.endswith(".gz"):
        return gzip.open(source, mode="rt", encoding="utf-8")
    return open(source, mode="rt", encoding="utf-8")


def clean_label(value, max_len=56):
    text = " ".join(str(value or "").split())
    if len(text) > max_len:
        text = text[: max_len - 1] + "…"
    return html.escape(text, quote=True)


def department_name(package):
    organization = package.get("organization") or {}
    return organization.get("name") or "Unknown"


def relation_url(relation):
    value = relation.get("related_url")
    if isinstance(value, dict):
        return value.get("en") or value.get("fr") or ""
    return value or ""


def target_ids(url):
    match = OPEN_CANADA_ID_RE.search(url or "")
    if not match:
        return None, None
    package_id = match.group(1).lower()
    resource_id = match.group(2).lower() if match.group(2) else None
    return package_id, resource_id


def target_node(url):
    package_id, resource_id = target_ids(url)
    if resource_id:
        return f"r:{resource_id}", package_id, resource_id
    if package_id:
        return f"p:{package_id}", package_id, None
    return f"u:{url}", None, None


def chart_filename(department):
    slug = re.sub(r"[^a-z0-9_-]+", "-", department.lower()).strip("-")
    return f"{slug or 'unknown'}.md"


def load_graph(source, limit=None):
    packages = {}
    resources = {}
    edges = []
    package_count = 0
    resource_count = 0

    with open_jsonl_source(source) as lines:
        for line in lines:
            if not line.strip():
                continue

            package = json.loads(line)
            package_count += 1
            package_id = str(package.get("id") or "").lower()
            owner = department_name(package)
            packages[package_id] = {
                "id": package_id,
                "department": owner,
                "title": package.get("title") or package.get("name") or package_id,
            }

            package_relationships = package.get("relationship") or []
            if isinstance(package_relationships, list):
                for relation in package_relationships:
                    url = relation_url(relation)
                    target, target_package, target_resource = target_node(url)
                    edges.append(
                        {
                            "level": "package",
                            "source": f"p:{package_id}",
                            "source_package": package_id,
                            "source_resource": "",
                            "source_department": owner,
                            "relation_type": relation.get("related_relationship") or "Unknown",
                            "target": target,
                            "target_package": target_package or "",
                            "target_resource": target_resource or "",
                            "target_url": url,
                        }
                    )

            resources_in_package = package.get("resources") or []
            resource_count += len(resources_in_package)
            for resource in resources_in_package:
                resource_id = str(resource.get("id") or "").lower()
                resources[resource_id] = {
                    "id": resource_id,
                    "package_id": package_id,
                    "department": owner,
                    "name": resource.get("name") or resource_id,
                    "format": resource.get("format") or "",
                }

                resource_relationships = resource.get("relationship") or []
                if not isinstance(resource_relationships, list):
                    continue

                for relation in resource_relationships:
                    url = relation_url(relation)
                    target, target_package, target_resource = target_node(url)
                    edges.append(
                        {
                            "level": "resource",
                            "source": f"r:{resource_id}",
                            "source_package": package_id,
                            "source_resource": resource_id,
                            "source_department": owner,
                            "relation_type": relation.get("related_relationship") or "Unknown",
                            "target": target,
                            "target_package": target_package or "",
                            "target_resource": target_resource or "",
                            "target_url": url,
                        }
                    )

            if limit is not None and package_count >= limit:
                break

    return {
        "packages": packages,
        "resources": resources,
        "edges": edges,
        "package_count": package_count,
        "resource_count": resource_count,
    }


def expanded_department_network(graph, department):
    seed_edges = [edge for edge in graph["edges"] if edge["source_department"] == department]
    seed_nodes = set()
    for edge in seed_edges:
        seed_nodes.add(edge["source"])
        seed_nodes.add(edge["target"])

    selected_edges = []
    selected_keys = set()
    for edge in graph["edges"]:
        if edge in seed_edges or edge["source"] in seed_nodes or edge["target"] in seed_nodes:
            key = (edge["level"], edge["source"], edge["relation_type"], edge["target"], edge["target_url"])
            if key in selected_keys:
                continue
            selected_edges.append(edge)
            selected_keys.add(key)
            seed_nodes.add(edge["source"])
            seed_nodes.add(edge["target"])

    package_nodes = set()
    resource_nodes = set()
    url_nodes = set()
    for node in seed_nodes:
        if node.startswith("r:"):
            resource_nodes.add(node)
            resource = graph["resources"].get(node[2:])
            if resource:
                package_nodes.add(f"p:{resource['package_id']}")
        elif node.startswith("p:"):
            package_nodes.add(node)
        else:
            url_nodes.add(node)

    for edge in selected_edges:
        if edge["target_package"]:
            package_nodes.add(f"p:{edge['target_package']}")

    return {
        "department": department,
        "seed_edges": sorted(
            seed_edges,
            key=lambda edge: (edge["level"], edge["source"], edge["relation_type"], edge["target"], edge["target_url"]),
        ),
        "edges": sorted(
            selected_edges,
            key=lambda edge: (edge["level"], edge["source"], edge["relation_type"], edge["target"], edge["target_url"]),
        ),
        "package_nodes": sorted(package_nodes),
        "resource_nodes": sorted(resource_nodes),
        "url_nodes": sorted(url_nodes),
    }


def node_department(node, graph):
    if node.startswith("p:"):
        return graph["packages"].get(node[2:], {}).get("department")
    if node.startswith("r:"):
        return graph["resources"].get(node[2:], {}).get("department")
    return None


def node_label(node, graph):
    if node.startswith("p:"):
        package = graph["packages"].get(node[2:], {})
        return (
            f"📦 {clean_label(package.get('department') or '?')} package<br/>"
            f"{clean_label(package.get('title') or node[2:])}<br/><code>{node[2:]}</code>"
        )

    if node.startswith("r:"):
        resource = graph["resources"].get(node[2:], {})
        format_label = resource.get("format") or ""
        return (
            f"📄 {clean_label(resource.get('department') or '?')} resource {clean_label(format_label, 12)}<br/>"
            f"{clean_label(resource.get('name') or node[2:])}<br/><code>{node[2:]}</code>"
        )

    url = node[2:] if node.startswith("u:") else node
    host = urlparse(url).netloc or "URL"
    return f"🔗 {clean_label(host, 32)}<br/>{clean_label(url, 40)}"


def mermaid_chart(network, graph):
    all_nodes = network["package_nodes"] + network["resource_nodes"] + network["url_nodes"]
    node_ids = {node: f"N{index}" for index, node in enumerate(all_nodes, start=1)}
    lines = [
        f"# {network['department']} Relationship Network",
        "",
        "```mermaid",
        "flowchart LR",
    ]

    for node in network["package_nodes"]:
        lines.append(f'  {node_ids[node]}(["{node_label(node, graph)}"])')
    for node in network["resource_nodes"]:
        lines.append(f'  {node_ids[node]}[["{node_label(node, graph)}"]]')
    for node in network["url_nodes"]:
        lines.append(f'  {node_ids[node]}{{"{node_label(node, graph)}"}}')

    for resource_node in network["resource_nodes"]:
        resource = graph["resources"].get(resource_node[2:])
        if not resource:
            continue
        package_node = f"p:{resource['package_id']}"
        if package_node in node_ids:
            lines.append(f"  {node_ids[package_node]} -. contains .-> {node_ids[resource_node]}")

    for edge in network["edges"]:
        if edge["source"] in node_ids and edge["target"] in node_ids:
            relation = clean_label(edge["relation_type"], 40)
            lines.append(f'  {node_ids[edge["source"]]} -- "{relation}" --> {node_ids[edge["target"]]}')

    for node in all_nodes:
        department = node_department(node, graph)
        if department == network["department"]:
            class_name = "seed"
        elif department:
            class_name = "other"
        else:
            class_name = "url"
        lines.append(f"  class {node_ids[node]} {class_name}")

    lines.extend(
        [
            "  classDef seed fill:#dbeafe,stroke:#1d4ed8,stroke-width:2px,color:#111827",
            "  classDef other fill:#ecfccb,stroke:#4d7c0f,stroke-width:1px,color:#111827",
            "  classDef url fill:#f3f4f6,stroke:#6b7280,stroke-dasharray: 4 3,color:#111827",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def write_if_changed(path, content):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_text(encoding="utf-8") == content:
        return False

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    tmp_path.replace(target)
    return True


def write_bytes_if_changed(path, content):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_bytes() == content:
        return False

    with tempfile.NamedTemporaryFile("wb", dir=target.parent, delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    tmp_path.replace(target)
    return True


def relation_type_counts(edges):
    counts = Counter(edge["relation_type"] for edge in edges)
    return json.dumps(dict(sorted(counts.items())), ensure_ascii=False, separators=(",", ":"))


def node_short_id(node):
    return node[2:10] if node.startswith(("p:", "r:")) else "url"


def overview_node_label(node, graph):
    department = node_department(node, graph)
    if node.startswith("p:"):
        return f"{department or '?'}\npackage\n{node_short_id(node)}"
    if node.startswith("r:"):
        resource = graph["resources"].get(node[2:], {})
        resource_format = resource.get("format") or "resource"
        return f"{department or '?'}\n{resource_format}\n{node_short_id(node)}"
    url = node[2:] if node.startswith("u:") else node
    host = urlparse(url).netloc or "URL"
    return f"external\n{host[:18]}"


def overview_graph_parts(graph):
    nodes = set()
    relation_edges = []
    containment_edges = []

    for edge in graph["edges"]:
        nodes.add(edge["source"])
        nodes.add(edge["target"])
        relation_edges.append((edge["source"], edge["target"], edge["relation_type"]))

    for node in list(nodes):
        if not node.startswith("r:"):
            continue
        resource = graph["resources"].get(node[2:])
        if not resource:
            continue
        package_node = f"p:{resource['package_id']}"
        nodes.add(package_node)
        containment_edges.append((package_node, node, "contains"))

    return sorted(nodes), relation_edges, containment_edges


def generate_overview_png(graph, path):
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
    except ImportError as exc:
        raise RuntimeError(
            "network overview image generation requires matplotlib and networkx"
        ) from exc

    nodes, relation_edges, containment_edges = overview_graph_parts(graph)
    network = nx.MultiDiGraph()
    network.add_nodes_from(nodes)
    for source, target, relation_type in relation_edges:
        network.add_edge(source, target, relation_type=relation_type, edge_kind="relation")
    for source, target, relation_type in containment_edges:
        network.add_edge(source, target, relation_type=relation_type, edge_kind="contains")

    plt.switch_backend("Agg")
    figure, axis = plt.subplots(figsize=(18, 12), dpi=180)
    axis.set_title("Open Canada package and resource relationship network", fontsize=18, pad=18)
    axis.axis("off")

    positions = nx.spring_layout(network, seed=42, k=1.2, iterations=250)
    relation_types = sorted({data["relation_type"] for _, _, data in network.edges(data=True)})
    relation_palette = {
        relation_type: plt.cm.tab20(index % 20)
        for index, relation_type in enumerate(relation_types)
    }

    package_nodes = [node for node in nodes if node.startswith("p:")]
    resource_nodes = [node for node in nodes if node.startswith("r:")]
    url_nodes = [node for node in nodes if node.startswith("u:")]

    nx.draw_networkx_nodes(
        network,
        positions,
        nodelist=package_nodes,
        node_shape="o",
        node_color="#dbeafe",
        edgecolors="#1d4ed8",
        linewidths=1.4,
        node_size=1700,
        ax=axis,
    )
    nx.draw_networkx_nodes(
        network,
        positions,
        nodelist=resource_nodes,
        node_shape="s",
        node_color="#dcfce7",
        edgecolors="#15803d",
        linewidths=1.2,
        node_size=1450,
        ax=axis,
    )
    nx.draw_networkx_nodes(
        network,
        positions,
        nodelist=url_nodes,
        node_shape="D",
        node_color="#f3f4f6",
        edgecolors="#6b7280",
        linewidths=1.0,
        node_size=1200,
        ax=axis,
    )

    relation_only_edges = [
        (source, target, key)
        for source, target, key, data in network.edges(keys=True, data=True)
        if data["edge_kind"] == "relation"
    ]
    relation_edge_colors = [
        relation_palette[network.get_edge_data(source, target, key)["relation_type"]]
        for source, target, key in relation_only_edges
    ]
    containment_only_edges = [
        (source, target, key)
        for source, target, key, data in network.edges(keys=True, data=True)
        if data["edge_kind"] == "contains"
    ]

    nx.draw_networkx_edges(
        network,
        positions,
        edgelist=relation_only_edges,
        edge_color=relation_edge_colors,
        arrows=True,
        arrowsize=14,
        width=1.7,
        alpha=0.82,
        connectionstyle="arc3,rad=0.08",
        ax=axis,
    )
    nx.draw_networkx_edges(
        network,
        positions,
        edgelist=containment_only_edges,
        edge_color="#9ca3af",
        arrows=False,
        width=1.0,
        alpha=0.45,
        style="dashed",
        ax=axis,
    )
    nx.draw_networkx_labels(
        network,
        positions,
        labels={node: overview_node_label(node, graph) for node in nodes},
        font_size=6.8,
        font_color="#111827",
        ax=axis,
    )

    legend_handles = [
        plt.Line2D([0], [0], marker="o", color="w", label="Package", markerfacecolor="#dbeafe", markeredgecolor="#1d4ed8", markersize=10),
        plt.Line2D([0], [0], marker="s", color="w", label="Resource", markerfacecolor="#dcfce7", markeredgecolor="#15803d", markersize=10),
        plt.Line2D([0], [0], marker="D", color="w", label="External URL", markerfacecolor="#f3f4f6", markeredgecolor="#6b7280", markersize=9),
        plt.Line2D([0], [0], color="#9ca3af", linestyle="--", label="Package contains resource"),
    ]
    for relation_type in relation_types:
        if relation_type == "contains":
            continue
        legend_handles.append(
            plt.Line2D([0], [0], color=relation_palette[relation_type], label=relation_type)
        )
    axis.legend(
        handles=legend_handles,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.08),
        ncol=4,
        fontsize=8,
        frameon=False,
    )
    figure.tight_layout()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        figure.savefig(tmp_path, format="png", bbox_inches="tight", facecolor="white")
        image_bytes = tmp_path.read_bytes()
    finally:
        plt.close(figure)
        tmp_path.unlink(missing_ok=True)

    return write_bytes_if_changed(path, image_bytes)


def network_departments(network, graph):
    departments = sorted(
        {
            node_department(node, graph)
            for node in network["package_nodes"] + network["resource_nodes"]
            if node_department(node, graph)
        }
    )
    return departments


def network_metrics(network, graph, run_date, chart_changed):
    edges = network["edges"]
    seed_edges = network["seed_edges"]
    departments = network_departments(network, graph)
    internal_edges = [
        edge for edge in edges
        if edge["target"].startswith(("p:", "r:"))
        and (edge["target_package"] in graph["packages"] or edge["target_resource"] in graph["resources"])
    ]
    external_edges = [edge for edge in edges if edge["target"].startswith("u:")]
    cross_department_edges = []
    for edge in edges:
        source_department = node_department(edge["source"], graph)
        target_department = node_department(edge["target"], graph)
        if source_department and target_department and source_department != target_department:
            cross_department_edges.append(edge)

    return {
        "date": run_date,
        "department": network["department"],
        "source_relation_edges": len(seed_edges),
        "expanded_relation_edges": len(edges),
        "package_relation_edges": sum(1 for edge in seed_edges if edge["level"] == "package"),
        "resource_relation_edges": sum(1 for edge in seed_edges if edge["level"] == "resource"),
        "total_nodes": len(network["package_nodes"]) + len(network["resource_nodes"]) + len(network["url_nodes"]),
        "package_nodes": len(network["package_nodes"]),
        "resource_nodes": len(network["resource_nodes"]),
        "url_nodes": len(network["url_nodes"]),
        "connected_departments_count": len(departments),
        "connected_departments": ";".join(departments),
        "internal_open_canada_edges": len(internal_edges),
        "external_url_edges": len(external_edges),
        "cross_department_edges": len(cross_department_edges),
        "relation_types": relation_type_counts(seed_edges),
        "chart_changed": "Y" if chart_changed else "N",
    }


def int_metric(row, key):
    return int(row.get(key) or 0)


def generated_readme_section(metrics, run_date, overview_png):
    if not metrics:
        return "No relationship networks were found in the metadata feed."

    total_departments = len(metrics)
    source_edges = sum(int_metric(row, "source_relation_edges") for row in metrics)
    expanded_edges = sum(int_metric(row, "expanded_relation_edges") for row in metrics)
    total_nodes = sum(int_metric(row, "total_nodes") for row in metrics)
    package_nodes = sum(int_metric(row, "package_nodes") for row in metrics)
    resource_nodes = sum(int_metric(row, "resource_nodes") for row in metrics)
    url_nodes = sum(int_metric(row, "url_nodes") for row in metrics)
    cross_department_edges = sum(int_metric(row, "cross_department_edges") for row in metrics)
    changed_charts = sum(1 for row in metrics if row.get("chart_changed") == "Y")

    top_rows = sorted(
        metrics,
        key=lambda row: (-int_metric(row, "total_nodes"), row["department"]),
    )[:10]
    top_table = [
        "| Department | Nodes | Source edges | Expanded edges | Connected departments |",
        "|---|---:|---:|---:|---|",
    ]
    for row in top_rows:
        top_table.append(
            "| {department} | {total_nodes} | {source_relation_edges} | "
            "{expanded_relation_edges} | {connected_departments} |".format(**row)
        )

    escaped_date = run_date.replace("-", "--")
    overview_path = Path(overview_png).name
    return "\n".join(
        [
            "[![Data Relationships Network Report](https://github.com/open-data/analytics-corporate-reporting/actions/workflows/data_rels_network_rpt.yml/badge.svg)](https://github.com/open-data/analytics-corporate-reporting/actions/workflows/data_rels_network_rpt.yml)",
            f"![Last updated](https://img.shields.io/badge/last%20updated-{escaped_date}-2f855a)",
            "",
            "[Open relationship stats in FlatGitHub](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=DATA_RELS_NETWORK_RPT/relationship_network_stats.csv)",
            "",
            f"![Overall relationship network]({overview_path})",
            "",
            "## Current Summary",
            "",
            f"- Last updated: `{run_date}`",
            f"- Departments with relationships: `{total_departments}`",
            f"- Source relationship edges: `{source_edges}`",
            f"- Expanded relationship edges: `{expanded_edges}`",
            f"- Rendered nodes across department charts: `{total_nodes}`",
            f"- Package nodes: `{package_nodes}`",
            f"- Resource nodes: `{resource_nodes}`",
            f"- External URL nodes: `{url_nodes}`",
            f"- Cross-department resolved edges: `{cross_department_edges}`",
            f"- Department chart files changed on this run: `{changed_charts}`",
            "",
            "## Largest Department Networks",
            "",
            "\n".join(top_table),
        ]
    )


def update_readme(path, report_markdown):
    target = Path(path)
    if target.exists():
        content = target.read_text(encoding="utf-8")
    else:
        content = "# Relationship Networks\n\n"

    block = f"{README_REPORT_START}\n{report_markdown}\n{README_REPORT_END}"
    if README_REPORT_START in content and README_REPORT_END in content:
        pattern = re.compile(
            rf"{re.escape(README_REPORT_START)}[\s\S]*?{re.escape(README_REPORT_END)}",
            re.MULTILINE,
        )
        content = pattern.sub(block, content, count=1)
    else:
        lines = content.splitlines()
        if lines and lines[0].startswith("# "):
            content = "\n".join([lines[0], "", block, "", *lines[1:]])
        else:
            content = f"{block}\n\n{content}"

    return write_if_changed(target, content if content.endswith("\n") else content + "\n")


def update_stats_csv(path, rows):
    fieldnames = [
        "date",
        "department",
        "source_relation_edges",
        "expanded_relation_edges",
        "package_relation_edges",
        "resource_relation_edges",
        "total_nodes",
        "package_nodes",
        "resource_nodes",
        "url_nodes",
        "connected_departments_count",
        "connected_departments",
        "internal_open_canada_edges",
        "external_url_edges",
        "cross_department_edges",
        "relation_types",
        "chart_changed",
    ]
    target = Path(path)
    existing = []
    if target.exists():
        with target.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                existing.append({field: row.get(field, "") for field in fieldnames})

    keyed = {(row["date"], row["department"]): row for row in existing}
    for row in rows:
        keyed[(row["date"], row["department"])] = {field: str(row.get(field, "")) for field in fieldnames}

    sorted_rows = sorted(keyed.values(), key=lambda row: (row["date"], row["department"]), reverse=False)
    sorted_rows = sorted(sorted_rows, key=lambda row: row["department"])
    sorted_rows = sorted(sorted_rows, key=lambda row: row["date"], reverse=True)

    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=target.parent, delete=False) as tmp:
        writer = csv.DictWriter(tmp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_rows)
        tmp_path = Path(tmp.name)
    tmp_path.replace(target)


def main():
    args = parse_args()
    run_date = args.date or date.today().isoformat()
    graph = load_graph(args.source, limit=args.limit)
    departments = sorted({edge["source_department"] for edge in graph["edges"]})

    chart_dir = Path(args.chart_dir)
    metrics = []
    changed_count = 0
    for department in departments:
        network = expanded_department_network(graph, department)
        chart = mermaid_chart(network, graph)
        changed = write_if_changed(chart_dir / chart_filename(department), chart)
        changed_count += 1 if changed else 0
        metrics.append(network_metrics(network, graph, run_date, changed))

    overview_changed = False
    if not args.skip_overview_image:
        overview_changed = generate_overview_png(graph, args.overview_png)

    readme_changed = False
    if not args.skip_readme:
        readme_changed = update_readme(
            args.readme,
            generated_readme_section(metrics, run_date, args.overview_png),
        )

    if not args.no_stats:
        update_stats_csv(args.stats_csv, metrics)

    print(f"Scanned {graph['package_count']} packages and {graph['resource_count']} resources.")
    print(f"Generated {len(departments)} department networks; {changed_count} chart files changed.")
    if not args.skip_overview_image:
        print(f"Updated {args.overview_png}: {'changed' if overview_changed else 'unchanged'}.")
    if not args.skip_readme:
        print(f"Updated {args.readme}: {'changed' if readme_changed else 'unchanged'}.")
    if not args.no_stats:
        print(f"Updated {args.stats_csv}.")


if __name__ == "__main__":
    main()
