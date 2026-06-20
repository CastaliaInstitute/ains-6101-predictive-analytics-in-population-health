#!/usr/bin/env python3
"""Create private student assignment repositories from a cohort template."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import (
    Runner,
    create_repo_from_template,
    grant_team_repo,
    module_code,
    read_roster,
    require_gh_token,
    require_slug,
    team_slug,
    validate_usernames,
    ensure_gh_available,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-org", required=True)
    parser.add_argument("--course-code", required=True, type=lambda v: require_slug(v, "course_code"))
    parser.add_argument("--cohort", required=True, type=lambda v: require_slug(v, "cohort"))
    parser.add_argument("--module", required=True, type=int)
    parser.add_argument("--roster-path", required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mod = module_code(args.module)
    ensure_gh_available()
    require_gh_token(args.dry_run)
    rows = read_roster(Path(args.roster_path))
    users = validate_usernames(row["github_username"] for row in rows)

    runner = Runner(dry_run=args.dry_run)
    instructor_team = team_slug(args.course_code, args.cohort, "instructors")
    template = f"{args.target_org}/{args.course_code}-{args.cohort}-{mod}-template"
    course_repo = f"{args.course_code}-{args.cohort}-course"

    for row, username in zip(rows, users, strict=True):
        repo = f"{args.course_code}-{args.cohort}-{mod}-{username.lower()}"
        runner.run(
            [
                "gh",
                "api",
                "-X",
                "PUT",
                f"repos/{args.target_org}/{course_repo}/collaborators/{username}",
                "-f",
                "permission=pull",
            ]
        )
        create_repo_from_template(runner, args.target_org, repo, template, private=True)
        grant_team_repo(runner, args.target_org, instructor_team, repo, "maintain")
        runner.run(
            [
                "gh",
                "api",
                "-X",
                "PUT",
                f"repos/{args.target_org}/{repo}/collaborators/{username}",
                "-f",
                "permission=push",
            ]
        )

    print("student repo provisioning plan complete" if args.dry_run else "student repo provisioning complete")


if __name__ == "__main__":
    main()
