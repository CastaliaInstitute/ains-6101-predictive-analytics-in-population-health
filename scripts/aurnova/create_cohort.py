#!/usr/bin/env python3
"""Create Aurnova cohort course and assignment template repositories."""

from __future__ import annotations

import argparse

from common import (
    Runner,
    add_team_member,
    create_or_update_team,
    create_repo_from_template,
    grant_team_repo,
    module_code,
    require_gh_token,
    require_slug,
    split_csv,
    team_slug,
    validate_usernames,
    ensure_gh_available,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-org", required=True)
    parser.add_argument("--course-code", required=True, type=lambda v: require_slug(v, "course_code"))
    parser.add_argument("--cohort", required=True, type=lambda v: require_slug(v, "cohort"))
    parser.add_argument("--canonical-course-repo", required=True)
    parser.add_argument("--assignment-template-prefix", required=True)
    parser.add_argument("--module-count", type=int, default=8)
    parser.add_argument("--instructor-github-users", default="")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.module_count < 1 or args.module_count > 24:
        raise SystemExit("--module-count must be between 1 and 24")

    instructors = validate_usernames(split_csv(args.instructor_github_users))
    ensure_gh_available()
    require_gh_token(args.dry_run)

    runner = Runner(dry_run=args.dry_run)
    instructor_team = team_slug(args.course_code, args.cohort, "instructors")

    create_or_update_team(
        runner,
        args.target_org,
        instructor_team,
        f"{args.course_code.upper()} {args.cohort} instructors",
    )

    course_repo = f"{args.course_code}-{args.cohort}-course"
    create_repo_from_template(
        runner,
        args.target_org,
        course_repo,
        args.canonical_course_repo,
        private=True,
    )
    grant_team_repo(runner, args.target_org, instructor_team, course_repo, "admin")

    for module in range(1, args.module_count + 1):
        mod = module_code(module)
        template_repo = f"{args.course_code}-{args.cohort}-{mod}-template"
        canonical_template = f"{args.assignment_template_prefix}{module:02d}"
        create_repo_from_template(
            runner,
            args.target_org,
            template_repo,
            canonical_template,
            private=True,
        )
        grant_team_repo(runner, args.target_org, instructor_team, template_repo, "admin")

    for username in instructors:
        add_team_member(runner, args.target_org, instructor_team, username)

    print("cohort provisioning plan complete" if args.dry_run else "cohort provisioning complete")


if __name__ == "__main__":
    main()
