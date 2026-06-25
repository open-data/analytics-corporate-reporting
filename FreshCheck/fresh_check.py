#!/usr/bin/env python3

import argparse
import gzip
import io
import json
import math
import os
import re
import sys
import tempfile
import urllib.request
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


DEFAULT_JSONL_GZ_URL = "https://open.canada.ca/static/od-do-canada.jsonl.gz"
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_JSON = SCRIPT_DIR / "freshness_tree.json"
DEFAULT_README = SCRIPT_DIR / "README.md"
REQUEST_TIMEOUT_SECONDS = int(os.environ.get("REQUEST_TIMEOUT_SECONDS", "60"))

GENERATED_START = "<!-- FRESHCHECK_REPORT_START -->"
GENERATED_END = "<!-- FRESHCHECK_REPORT_END -->"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build FreshCheck metadata freshness outputs from the Open Canada JSONL feed."
    )
    parser.add_argument(
        "--source",
        default=DEFAULT_JSONL_GZ_URL,
        help="Source JSONL or JSONL.GZ path/URL. Defaults to the Open Canada metadata feed.",
    )
    parser.add_argument(
        "--output-json",
        default=DEFAULT_OUTPUT_JSON,
        help="Path for the hierarchical freshness JSON output. Must be inside the FreshCheck directory.",
    )
    parser.add_argument(
        "--readme",
        default=DEFAULT_README,
        help="README path to update between FreshCheck report markers. Must be inside the FreshCheck directory.",
    )
    parser.add_argument(
        "--today",
        default=None,
        help="Override current date for tests, in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional maximum number of packages to process, for local smoke tests.",
    )
    parser.add_argument(
        "--skip-readme",
        action="store_true",
        help="Write JSON only and do not update the README.",
    )
    return parser.parse_args()


def resolve_freshcheck_output_path(path):
    """Resolve an output path and ensure it stays inside this FreshCheck directory."""
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        parts = candidate.parts
        if parts and parts[0] == SCRIPT_DIR.name:
            candidate = Path(*parts[1:]) if len(parts) > 1 else Path(".")
        candidate = SCRIPT_DIR / candidate

    resolved = candidate.resolve()
    try:
        resolved.relative_to(SCRIPT_DIR)
    except ValueError as exc:
        raise ValueError(f"Output path must be inside {SCRIPT_DIR}: {path}") from exc
    return resolved


def parse_datetime(value):
    if not value:
        return None

    text = str(value).strip()
    if not text:
        return None

    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def days_in_month(year, month):
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    return (next_month - date(year, month, 1)).days


def add_months(start_date, months):
    month_index = start_date.month - 1 + months
    year = start_date.year + month_index // 12
    month = month_index % 12 + 1
    day = min(start_date.day, days_in_month(year, month))
    return start_date.replace(year=year, month=month, day=day)


def parse_iso8601_duration(value):
    """
    Parse the date component of CKAN ISO 8601 frequency values.

    Supported examples: P1D, P1W, P1M, P3M, P6M, P1Y. Time components are not
    expected in the feed and are intentionally ignored if present.
    """
    if not value:
        return None

    match = re.fullmatch(
        r"P(?:(?P<years>\d+(?:\.\d+)?)Y)?(?:(?P<months>\d+(?:\.\d+)?)M)?"
        r"(?:(?P<weeks>\d+(?:\.\d+)?)W)?(?:(?P<days>\d+(?:\.\d+)?)D)?"
        r"(?:T.*)?",
        str(value).strip().upper(),
    )
    if not match:
        return None

    parts = {
        key: float(raw_value) if raw_value is not None else 0.0
        for key, raw_value in match.groupdict().items()
    }
    if not any(parts.values()):
        return None

    return parts


def expected_date_from(modified_value, frequency):
    modified = parse_datetime(modified_value)
    duration = parse_iso8601_duration(frequency)
    if modified is None or duration is None:
        return None

    modified_date = modified.date()
    whole_months = int(duration["years"] * 12 + duration["months"])
    expected = add_months(modified_date, whole_months) if whole_months else modified_date

    extra_days = duration["weeks"] * 7 + duration["days"]
    if extra_days:
        expected += timedelta(days=math.ceil(extra_days))

    return expected


def freshness_status(days_until_expected):
    if days_until_expected is None:
        return "unknown"
    if days_until_expected < 0:
        return "late"
    if days_until_expected <= 7:
        return "due_soon"
    return "current"


def freshness_record(modified_value, frequency, today):
    expected = expected_date_from(modified_value, frequency)
    if expected is None:
        days_until_expected = None
    else:
        days_until_expected = (expected - today).days

    return {
        "expected_update_date": expected.isoformat() if expected else None,
        "days_until_expected_update": days_until_expected,
        "freshness_status": freshness_status(days_until_expected),
    }


def open_jsonl_source(source):
    if source.startswith("http://") or source.startswith("https://"):
        response = urllib.request.urlopen(source, timeout=REQUEST_TIMEOUT_SECONDS)
        if source.endswith(".gz"):
            return gzip.open(response, mode="rt", encoding="utf-8")
        return io.TextIOWrapper(response, encoding="utf-8")

    if source.endswith(".gz"):
        return gzip.open(source, mode="rt", encoding="utf-8")
    else:
        return open(source, mode="rt", encoding="utf-8")


def owner_name(package):
    organization = package.get("organization") or {}
    return organization.get("name") or "Unknown"


def owner_title(package):
    organization = package.get("organization") or {}
    return organization.get("title")


def resource_modified(resource):
    return resource.get("metadata_modified") or resource.get("last_modified") or resource.get("created")


def build_resource(resource, frequency, today):
    modified = resource_modified(resource)
    record = {
        "id": resource.get("id"),
        "name": resource.get("name"),
        "format": resource.get("format"),
        "metadata_modified": resource.get("metadata_modified"),
        "last_modified": resource.get("last_modified"),
        "created": resource.get("created"),
    }
    record.update(freshness_record(modified, frequency, today))
    return record


def build_package(package, today):
    frequency = package.get("frequency")
    package_record = {
        "name": owner_name(package),
        "organization_title": owner_title(package),
        "id": package.get("id"),
        "package_name": package.get("name"),
        "title": package.get("title"),
        "metadata_created": package.get("metadata_created"),
        "metadata_modified": package.get("metadata_modified"),
        "frequency": frequency,
        "resources": [],
    }
    package_record.update(freshness_record(package.get("metadata_modified"), frequency, today))

    resources = package.get("resources") or []
    package_record["resources"] = sorted(
        [build_resource(resource, frequency, today) for resource in resources],
        key=lambda item: (
            item.get("freshness_status") or "",
            item.get("days_until_expected_update") is None,
            item.get("days_until_expected_update") if item.get("days_until_expected_update") is not None else 0,
            item.get("id") or "",
        ),
    )
    return package_record


def iter_packages(source, limit=None):
    count = 0
    with open_jsonl_source(source) as lines:
        for line in lines:
            if not line.strip():
                continue
            yield json.loads(line)
            count += 1
            if limit is not None and count >= limit:
                return


def build_tree(source, today, limit=None):
    packages = [build_package(package, today) for package in iter_packages(source, limit=limit)]
    packages.sort(
        key=lambda item: (
            item.get("name") or "",
            item.get("id") or "",
        )
    )
    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "as_of_date": today.isoformat(),
        "source": source,
        "packages": packages,
    }


def package_days(package):
    return package.get("days_until_expected_update")


def status_bucket(days_until_expected):
    if days_until_expected is None:
        return "Unknown"
    if days_until_expected < -365:
        return "Late > 1 year"
    if days_until_expected < -90:
        return "Late 91-365 days"
    if days_until_expected < -30:
        return "Late 31-90 days"
    if days_until_expected < -7:
        return "Late 8-30 days"
    if days_until_expected < 0:
        return "Late 1-7 days"
    if days_until_expected <= 7:
        return "Due in 0-7 days"
    if days_until_expected <= 30:
        return "Due in 8-30 days"
    return "Current > 30 days"


def sort_counter_items(counter, order=None):
    if order:
        order_index = {value: index for index, value in enumerate(order)}
        return sorted(counter.items(), key=lambda item: (order_index.get(item[0], len(order_index)), item[0]))
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))


def mermaid_pie(title, items):
    rows = ["```mermaid", f"pie showData title {title}"]
    for label, count in items:
        escaped = str(label).replace('"', r'\"')
        rows.append(f'    "{escaped}": {int(count)}')
    rows.append("```")
    return "\n".join(rows)


def mermaid_bar(title, x_labels, values, y_axis):
    safe_labels = [str(label).replace('"', r'\"') for label in x_labels]
    safe_values = [str(int(round(value))) for value in values]
    return "\n".join(
        [
            "```mermaid",
            "xychart-beta",
            f'    title "{title}"',
            "    x-axis [" + ", ".join(f'"{label}"' for label in safe_labels) + "]",
            f'    y-axis "{y_axis}" 0 --> 100',
            "    bar [" + ", ".join(safe_values) + "]",
            "```",
        ]
    )


def report_summary(tree):
    packages = tree["packages"]
    resources = [resource for package in packages for resource in package.get("resources", [])]

    package_statuses = Counter(package.get("freshness_status", "unknown") for package in packages)
    resource_statuses = Counter(resource.get("freshness_status", "unknown") for resource in resources)
    buckets = Counter(status_bucket(package_days(package)) for package in packages)

    org_stats = defaultdict(lambda: {"total": 0, "current": 0, "late": 0, "days_sum": 0, "days_count": 0})
    for package in packages:
        org = package.get("name") or "Unknown"
        days = package_days(package)
        stats = org_stats[org]
        stats["total"] += 1
        if package.get("freshness_status") == "current":
            stats["current"] += 1
        if package.get("freshness_status") == "late":
            stats["late"] += 1
        if days is not None:
            stats["days_sum"] += days
            stats["days_count"] += 1

    org_rows = []
    for org, stats in org_stats.items():
        if stats["total"] < 5:
            continue
        current_percent = 100 * stats["current"] / stats["total"]
        average_days = stats["days_sum"] / stats["days_count"] if stats["days_count"] else None
        org_rows.append(
            {
                "org": org,
                "total": stats["total"],
                "current_percent": current_percent,
                "late": stats["late"],
                "average_days_until_expected_update": average_days,
            }
        )

    org_rows.sort(key=lambda item: (-item["current_percent"], -item["total"], item["org"]))
    return {
        "package_count": len(packages),
        "resource_count": len(resources),
        "package_statuses": package_statuses,
        "resource_statuses": resource_statuses,
        "buckets": buckets,
        "top_current_orgs": org_rows[:15],
    }


def markdown_report(tree):
    summary = report_summary(tree)
    bucket_order = [
        "Late > 1 year",
        "Late 91-365 days",
        "Late 31-90 days",
        "Late 8-30 days",
        "Late 1-7 days",
        "Due in 0-7 days",
        "Due in 8-30 days",
        "Current > 30 days",
        "Unknown",
    ]

    top_orgs = summary["top_current_orgs"]
    org_chart = "No organizations met the minimum package count for this chart."
    if top_orgs:
        org_chart = mermaid_bar(
            "Departments with highest current package share",
            [row["org"] for row in top_orgs],
            [row["current_percent"] for row in top_orgs],
            "Current packages (%)",
        )

    lines = [
        f"Generated at: `{tree['generated_at']}`",
        f"As of date: `{tree['as_of_date']}`",
        f"Packages assessed: `{summary['package_count']}`",
        f"Resources assessed: `{summary['resource_count']}`",
        "",
        "### Package Freshness Status",
        mermaid_pie("Package freshness status", sort_counter_items(summary["package_statuses"])),
        "",
        "### Resource Freshness Status",
        mermaid_pie("Resource freshness status", sort_counter_items(summary["resource_statuses"])),
        "",
        "### Package Update Timing",
        mermaid_pie("Package timing against expected update date", sort_counter_items(summary["buckets"], order=bucket_order)),
        "",
        "### Departments Keeping Data Current",
        org_chart,
    ]
    return "\n".join(lines)


def replace_generated_section(readme_path, report):
    readme = Path(readme_path)
    if readme.exists():
        content = readme.read_text(encoding="utf-8")
    else:
        content = "# FreshCheck\n\n"

    generated_block = f"{GENERATED_START}\n{report}\n{GENERATED_END}"
    if GENERATED_START in content and GENERATED_END in content:
        pattern = re.compile(
            rf"{re.escape(GENERATED_START)}[\s\S]*?{re.escape(GENERATED_END)}",
            re.MULTILINE,
        )
        content = pattern.sub(generated_block, content, count=1)
    else:
        if content and not content.endswith("\n"):
            content += "\n"
        content += "\n" + generated_block + "\n"

    readme.parent.mkdir(parents=True, exist_ok=True)
    readme.write_text(content, encoding="utf-8")


def atomic_write_json(path, data):
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output_path.parent, delete=False) as tmp:
        json.dump(data, tmp, ensure_ascii=False, indent=2)
        tmp.write("\n")
        tmp_path = Path(tmp.name)
    tmp_path.replace(output_path)


def main():
    args = parse_args()
    today = date.fromisoformat(args.today) if args.today else date.today()
    output_json = resolve_freshcheck_output_path(args.output_json)
    readme = resolve_freshcheck_output_path(args.readme)

    tree = build_tree(args.source, today, limit=args.limit)
    atomic_write_json(output_json, tree)

    if not args.skip_readme:
        replace_generated_section(readme, markdown_report(tree))

    print(f"Wrote {output_json}")
    if not args.skip_readme:
        print(f"Updated {readme}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
