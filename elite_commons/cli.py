"""Command-line interface for the static ELITE tool catalogue."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "catalog" / "tools.json"

def load_catalogue() -> dict:
    return json.loads(CATALOGUE.read_text(encoding="utf-8"))

def validate(data: dict) -> list[str]:
    errors = []
    if data.get("schema_version") != "1.0.0":
        errors.append("unsupported schema_version")
    ids = set()
    for i, item in enumerate(data.get("tools", [])):
        for field in ("id", "name", "url", "capabilities", "inputs", "outputs", "status", "evidence"):
            if field not in item:
                errors.append(f"tools[{i}] missing {field}")
        if item.get("id") in ids:
            errors.append(f"duplicate id: {item.get('id')}")
        ids.add(item.get("id"))
        parsed = urlparse(item.get("url", ""))
        if parsed.scheme != "https" or parsed.netloc != "github.com":
            errors.append(f"tools[{i}] URL must use https://github.com")
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
