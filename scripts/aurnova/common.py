#!/usr/bin/env python3
"""Shared helpers for Aurnova course provisioning scripts."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,48}[a-z0-9]$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")


def require_slug(value: str, label: str) -> str:
    if not SLUG_RE.fullmatch(value):
        raise argparse.ArgumentTypeError(
            f"{label} must be lowercase, URL-safe, and 3-50 characters: {value!r}"
        )
    return value


def module_code(module: int) -> str:
    if module < 1 or module > 99:
        raise argparse.ArgumentTypeError("module must be between 1 and 99")
    return f"m{module:02d}"


def split_csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def validate_usernames(users: Iterable[str]) -> list[str]:
    valid = []
    for user in users:
        if not USERNAME_RE.fullmatch(user):
            raise argparse.ArgumentTypeError(f"Invalid GitHub username: {user!r}")
        valid.append(user)
    return valid


@dataclass
class Runner:
    dry_run: bool

    def run(self, args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str] | None:
        print("+", " ".join(args))
        if self.dry_run:
            return None
        return subprocess.run(args, check=check, text=True, capture_output=False)

    def gh_json(self, args: list[str], *, check: bool = True) -> dict | list | None:
        print("+", " ".join(args))
        if self.dry_run:
            return None
        result = subprocess.run(args, check=check, text=True, capture_output=True)
        if not result.stdout.strip():
            return {}
        return json.loads(result.stdout)


def require_gh_token(dry_run: bool) -> None:
    if dry_run:
        return
    if not os.environ.get("GH_TOKEN") and not os.environ.get("GITHUB_TOKEN"):
        raise SystemExit("GH_TOKEN or GITHUB_TOKEN is required when dry_run is false")


def ensure_gh_available() -> None:
    try:
        subprocess.run(["gh", "--version"], check=True, capture_output=True, text=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise SystemExit("GitHub CLI `gh` is required for provisioning") from exc


def team_slug(course_code: str, cohort: str, role: str) -> str:
    return f"{course_code}-{cohort}-{role}"


def create_or_update_team(runner: Runner, org: str, name: str, description: str) -> None:
    slug = name.lower().replace("_", "-")
    existing = runner.gh_json(
        ["gh", "api", f"orgs/{org}/teams/{slug}", "--silent"],
        check=False,
    )
    if existing is None and runner.dry_run:
        print(f"dry-run: would ensure team {org}/{slug}")
        return
    if existing:
        print(f"team exists: {org}/{slug}")
        return
    runner.run(
        [
            "gh",
            "api",
            "-X",
            "POST",
            f"orgs/{org}/teams",
            "-f",
            f"name={name}",
            "-f",
            "privacy=closed",
            "-f",
            f"description={description}",
        ]
    )


def grant_team_repo(runner: Runner, org: str, team: str, repo: str, permission: str) -> None:
    runner.run(
        [
            "gh",
            "api",
            "-X",
            "PUT",
            f"orgs/{org}/teams/{team}/repos/{org}/{repo}",
            "-f",
            f"permission={permission}",
        ]
    )


def add_team_member(runner: Runner, org: str, team: str, username: str, role: str = "member") -> None:
    runner.run(
        [
            "gh",
            "api",
            "-X",
            "PUT",
            f"orgs/{org}/teams/{team}/memberships/{username}",
            "-f",
            f"role={role}",
        ]
    )


def create_repo_from_template(
    runner: Runner,
    org: str,
    repo: str,
    template: str,
    *,
    private: bool = True,
) -> None:
    existing = runner.gh_json(["gh", "repo", "view", f"{org}/{repo}", "--json", "name"], check=False)
    if existing is None and runner.dry_run:
        print(f"dry-run: would ensure repo {org}/{repo} from template {template}")
    elif existing:
        print(f"repo exists: {org}/{repo}")
        return
    visibility_flag = "--private" if private else "--public"
    runner.run(
        [
            "gh",
            "repo",
            "create",
            f"{org}/{repo}",
            visibility_flag,
            "--template",
            template,
            "--clone=false",
        ]
    )


def read_roster(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Roster file not found: {path}")
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    required = {"student_id", "name", "github_username", "email"}
    missing = required - set(rows[0].keys() if rows else [])
    if missing:
        raise SystemExit(f"Roster file missing columns: {', '.join(sorted(missing))}")
    return rows


def write_roster(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["student_id", "name", "github_username", "email"]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    print("common.py is a helper module", file=sys.stderr)
    raise SystemExit(2)
