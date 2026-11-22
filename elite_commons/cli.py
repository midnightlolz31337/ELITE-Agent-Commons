"""Command-line interface for the static ELITE tool catalogue."""
from __future__ import annotations
import argparse
import json
from importlib.resources import files
from urllib.parse import urlparse

CATALOGUE = files("elite_commons").joinpath("data", "tools.json")

def load_catalogue() -> dict:
    return json.loads(CATALOGUE.read_text(encoding="utf-8"))

def validate(data: dict) -> list[str]:
    errors = []
    if not isinstance(data, dict):
        return ["catalogue must be a JSON object"]
    if data.get("schema_version") != "1.0.0":
        errors.append("unsupported schema_version")
    tools = data.get("tools")
    if not isinstance(tools, list):
        return errors + ["tools must be a list"]

    ids = set()
    allowed_statuses = {"prototype", "specification", "scaffolded", "implemented", "experimental", "planned", "deprecated"}
    string_fields = ("id", "name", "url", "status", "evidence")
    list_fields = ("capabilities", "inputs", "outputs")

    for i, item in enumerate(tools):
        if not isinstance(item, dict):
            errors.append(f"tools[{i}] must be an object")
            continue
        for field in (*string_fields, *list_fields):
            if field not in item:
                errors.append(f"tools[{i}] missing {field}")

        for field in string_fields:
            value = item.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"tools[{i}] {field} must be a non-empty string")

        for field in list_fields:
            value = item.get(field)
            if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
                errors.append(f"tools[{i}] {field} must be a list of non-empty strings")

        item_id = item.get("id")
        if isinstance(item_id, str) and item_id:
            if item_id in ids:
                errors.append(f"duplicate id: {item_id}")
            ids.add(item_id)

        status = item.get("status")
        if isinstance(status, str) and status not in allowed_statuses:
            errors.append(f"tools[{i}] unsupported status: {status}")

        url = item.get("url")
        if isinstance(url, str):
            parsed = urlparse(url)
            segments = [part for part in parsed.path.split("/") if part]
            if (parsed.scheme != "https" or parsed.netloc != "github.com"
                    or len(segments) != 2 or parsed.username or parsed.password
                    or parsed.query or parsed.fragment):
                errors.append(f"tools[{i}] URL must be a canonical https://github.com/owner/repo URL")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(prog="elite-commons")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    search = sub.add_parser("search")
    search.add_argument("term")
    route = sub.add_parser("route")
    route.add_argument("task")
    sub.add_parser("validate")
    args = parser.parse_args()
    data = load_catalogue()
    tools = data.get("tools", [])
    if args.command == "validate":
        errors = validate(data)
        if errors:
            print("\n".join("ERROR: " + e for e in errors))
            return 1
        print(f"OK: {len(tools)} tools validated")
        return 0
    if args.command == "list":
        for item in tools:
            print(f"{item['id']} — {item['name']} [{item['status']}]")
        return 0
    term = args.term if args.command == "search" else args.task
    words = set(term.casefold().split())
    scored = []
    for item in tools:
        corpus = " ".join([item["name"], *item["capabilities"], *item["inputs"], *item["outputs"]]).casefold()
        score = sum(1 for word in words if word in corpus)
        if score:
            scored.append((score, item))
    for score, item in sorted(scored, key=lambda pair: (-pair[0], pair[1]["id"])):
        print(f"{score}  {item['name']} — {item['url']}")
        print("   capabilities: " + ", ".join(item["capabilities"]))
    if not scored:
        print("No catalogue match. Do not infer that no suitable tool exists.")
    if args.command == "route":
        print("Review the candidate manually. This command does not execute or authorize it.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
