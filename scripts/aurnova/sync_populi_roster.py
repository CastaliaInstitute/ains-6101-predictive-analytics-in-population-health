#!/usr/bin/env python3
"""Fetch a Populi roster into a normalized CSV.

The Populi API endpoint shape should be validated against the target tenant before
production use. This script centralizes the expected output contract used by the
GitHub provisioning scripts.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from common import write_roster


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--course-offering-id", required=True)
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def fetch_json(url: str, api_key: str) -> dict | list:
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_rows(payload: dict | list) -> list[dict[str, str]]:
    if isinstance(payload, dict):
        records = payload.get("data") or payload.get("results") or payload.get("students") or []
    else:
        records = payload
    rows = []
    for record in records:
        person = record.get("person") or record.get("student") or record
        github_username = (
            person.get("github_username")
            or person.get("github")
            or person.get("custom_fields", {}).get("github_username")
            or ""
        )
        rows.append(
            {
                "student_id": str(person.get("student_id") or person.get("visible_student_id") or person.get("id") or ""),
                "name": str(person.get("name") or person.get("display_name") or ""),
                "github_username": str(github_username),
                "email": str(person.get("email") or person.get("primary_email") or ""),
            }
        )
    return rows


def main() -> None:
    args = parse_args()
    base = os.environ.get("POPULI_API_BASE", "").rstrip("/")
    api_key = os.environ.get("POPULI_API_KEY", "")
    if not base or not api_key:
        raise SystemExit("POPULI_API_BASE and POPULI_API_KEY are required")

    url = f"{base}/api2/courseofferings/{args.course_offering_id}/students"
    print(f"Fetching Populi roster: {url}")
    try:
        payload = fetch_json(url, api_key)
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"Populi API request failed: HTTP {exc.code}") from exc

    rows = normalize_rows(payload)
    missing_github = [row for row in rows if not row["github_username"]]
    print(f"students={len(rows)} missing_github_username={len(missing_github)}")
    if missing_github:
        print("Rows without GitHub usernames must be resolved before repo provisioning.")

    if args.dry_run:
        for row in rows[:5]:
            print(row)
        print("dry-run: roster not written")
        return

    write_roster(Path(args.output_path), rows)
    print(f"wrote {args.output_path}")


if __name__ == "__main__":
    main()
