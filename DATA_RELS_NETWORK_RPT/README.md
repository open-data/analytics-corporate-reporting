# Relationship Networks

This report scans the Open Canada metadata JSONL feed and builds one Mermaid
network chart for each department that has package-level or resource-level
relationships.

The generator writes:

| Path | Purpose |
|---|---|
| `DATA_RELS_NETWORK_RPT/charts/*.md` | One Mermaid chart per source department with relationships. |
| `DATA_RELS_NETWORK_RPT/relationship_network_stats.csv` | Daily department metrics sorted by `date` descending and `department` ascending. |

Run locally:

```bash
python3 DATA_RELS_NETWORK_RPT/relationship_network.py
```

Smoke test without touching repo outputs:

```bash
tmp_dir="$(mktemp -d)"
python3 DATA_RELS_NETWORK_RPT/relationship_network.py \
  --limit 100 \
  --chart-dir "$tmp_dir/charts" \
  --stats-csv "$tmp_dir/relationship_network_stats.csv"
rm -rf "$tmp_dir"
```

Chart files are only rewritten when the department network content changes. The
stats CSV replaces the current date and department row on rerun, then sorts by
date descending and department ascending.

Metrics collected:

| Column | Meaning |
|---|---|
| `source_relation_edges` | Outgoing relationship records originating from the department. |
| `expanded_relation_edges` | Relationship records included after adding directly connected nodes. |
| `package_relation_edges` | Source department relationship records from package-level metadata. |
| `resource_relation_edges` | Source department relationship records from resource-level metadata. |
| `total_nodes` | Package, resource, and URL nodes in the rendered chart. |
| `package_nodes` | Package nodes in the rendered chart. |
| `resource_nodes` | Resource nodes in the rendered chart. |
| `url_nodes` | External or unresolved URL nodes in the rendered chart. |
| `connected_departments_count` | Count of departments represented in resolved package/resource nodes. |
| `connected_departments` | Semicolon-separated resolved departments represented in the chart. |
| `internal_open_canada_edges` | Chart edges that resolve to Open Canada package/resource nodes. |
| `external_url_edges` | Chart edges that point to unresolved or external URLs. |
| `cross_department_edges` | Chart edges whose resolved source and target departments differ. |
| `relation_types` | JSON object of source relationship type counts. |
| `chart_changed` | `Y` if the chart file content changed on this run, otherwise `N`. |
