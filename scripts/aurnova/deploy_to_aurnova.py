#!/usr/bin/env python3
"""Deploy the Castalia course source into an Aurnova instructor repository.

The deployment copy is intentionally sanitized:

- local build/runtime directories are excluded
- Castalia-specific Pages CNAME is removed; customer DNS is not configured
- cohort workflow defaults are pointed at the Aurnova instructor repo

By default the script runs in dry-run mode. Use --live to create/push the target
repository.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "_build",
    "site",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}
TEXT_SUFFIXES = {".md", ".html", ".yml", ".yaml", ".json", ".txt", ".css"}


def run(args: list[str], cwd: Path, *, dry_run: bool = False) -> None:
    print("+", " ".join(args))
    if dry_run:
        return
    subprocess.run(args, cwd=cwd, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-org", default="Aurnova")
    parser.add_argument("--target-repo", default="ain6003-instructor")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--visibility", choices=["private", "public", "internal"], default="private")
    parser.add_argument("--live", action="store_true", help="Create/push the target repository")
    parser.add_argument("--force", action="store_true", help="Use --force-with-lease when pushing")
    parser.add_argument("--enable-pages", action="store_true", help="Keep Pages workflow and enable workflow-based Pages")
    parser.add_argument("--include-exports", action="store_true", help="Keep PDF/EPUB export workflow")
    parser.add_argument("--skip-build", action="store_true", help="Skip make site validation")
    parser.add_argument("--keep-workdir", action="store_true", help="Keep the temporary deployment directory")
    return parser.parse_args()


def should_copy(path: Path) -> bool:
    if any(part in EXCLUDE_DIRS for part in path.parts):
        return False
    if path.suffix in EXCLUDE_SUFFIXES:
        return False
    if path.name == ".DS_Store":
        return False
    return True


def copy_source(dest: Path) -> None:
    for src in ROOT.rglob("*"):
        rel = src.relative_to(ROOT)
        if not should_copy(rel):
            continue
        target = dest / rel
        if src.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)


def replace_text(path: Path, replacements: dict[str, str]) -> None:
    if not path.exists():
        return
    text = path.read_text()
    for old, new in replacements.items():
        text = text.replace(old, new)
    path.write_text(text)


def sanitize(dest: Path, target_org: str, target_repo: str, *, enable_pages: bool, include_exports: bool) -> None:
    remove_paths = [
        "pages/CNAME",
        "docs/CUSTOM_DOMAIN.md",
        "scripts/cf-dns-ains6003-github-pages.sh",
        ".github/workflows/sync-dns.yml",
        ".github/workflows/fulfill-aurnova-purchase.yml",
    ]
    if not enable_pages:
        remove_paths.append(".github/workflows/pages.yml")
    if not include_exports:
        remove_paths.append(".github/workflows/exports.yml")
    for rel in remove_paths:
        path = dest / rel
        if path.exists():
            path.unlink()

    canonical = f"{target_org}/{target_repo}"
    replacements = {
        "Aurnova/ain6003-course": canonical,
        "aurnova/ain6003-course": canonical,
        "CastaliaInstitute/ains-6003-deep-learning-and-neural-networks": canonical,
        "https://github.com/CastaliaInstitute/ains-6003-deep-learning-and-neural-networks": f"https://github.com/{canonical}",
        "https://codespaces.new/CastaliaInstitute/ains-6003-deep-learning-and-neural-networks": f"https://codespaces.new/{canonical}",
        "https://castaliainstitute.github.io/ains-6003-deep-learning-and-neural-networks/": "Aurnova private Pages URL",
        "Cloudflare-proxied CNAME \u2192 GitHub Pages": "private GitHub Pages in Aurnova",
        "https://ains6003.courses.castalia.institute/": "Aurnova private Pages URL",
        "See [docs/CUSTOM_DOMAIN.md](docs/CUSTOM_DOMAIN.md) for DNS, TLS, and Zero Trust Access.": "Customer DNS, custom domains, and HTTPS policy are handled outside this instructor repository.",
        "- `.github/workflows/fulfill-aurnova-purchase.yml`\n": "",
    }
    for path in dest.rglob("*"):
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            replace_text(path, replacements)


def repo_exists(owner: str, repo: str) -> bool:
    result = subprocess.run(
        ["gh", "repo", "view", f"{owner}/{repo}", "--json", "name"],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def create_or_confirm_repo(args: argparse.Namespace, dry_run: bool) -> None:
    full_name = f"{args.target_org}/{args.target_repo}"
    if repo_exists(args.target_org, args.target_repo):
        print(f"repo exists: {full_name}")
        return
    visibility_flag = f"--{args.visibility}"
    run(
        [
            "gh",
            "repo",
            "create",
            full_name,
            visibility_flag,
            "--description",
            "AINS6003 instructor-facing course repository",
            "--disable-wiki",
        ],
        ROOT,
        dry_run=dry_run,
    )


def ensure_pages_enabled(args: argparse.Namespace, dry_run: bool) -> None:
    full_name = f"{args.target_org}/{args.target_repo}"
    result = subprocess.run(
        ["gh", "api", f"repos/{full_name}/pages"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        print(f"pages exists: {full_name}")
        run(
            ["gh", "api", "-X", "PUT", f"repos/{full_name}/pages", "-f", "build_type=workflow"],
            ROOT,
            dry_run=dry_run,
        )
        return
    run(
        ["gh", "api", "-X", "POST", f"repos/{full_name}/pages", "-f", "build_type=workflow"],
        ROOT,
        dry_run=dry_run,
    )


def clean_checkout(dest: Path) -> None:
    for path in dest.iterdir():
        if path.name == ".git":
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def has_changes(dest: Path) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=dest,
        text=True,
        capture_output=True,
        check=True,
    )
    return bool(result.stdout.strip())


def git_commit_and_push(dest: Path, args: argparse.Namespace, dry_run: bool, *, existing_repo: bool) -> None:
    remote = f"https://github.com/{args.target_org}/{args.target_repo}.git"
    if not existing_repo:
        run(["git", "init", "-b", args.branch], dest, dry_run=dry_run)
    run(["git", "config", "user.name", "aurnova-deploy"], dest, dry_run=dry_run)
    run(["git", "config", "user.email", "automation@aurnova.ai"], dest, dry_run=dry_run)
    run(["git", "add", "."], dest, dry_run=dry_run)
    if not dry_run and not has_changes(dest):
        print("no deployment changes to commit")
        return
    run(["git", "commit", "-m", "Deploy AINS6003 instructor course"], dest, dry_run=dry_run)
    if not existing_repo:
        run(["git", "remote", "add", "origin", remote], dest, dry_run=dry_run)
    push = ["git", "push", "origin", args.branch]
    if args.force:
        push.append("--force-with-lease")
    run(push, dest, dry_run=dry_run)


def main() -> None:
    args = parse_args()
    dry_run = not args.live

    if not args.skip_build:
        run(["make", "site"], ROOT, dry_run=False)

    root_workdir = Path(tempfile.mkdtemp(prefix="ain6003-aurnova-deploy-"))
    workdir = root_workdir / "repo"
    try:
        print(f"deployment workdir: {root_workdir}")
        exists = repo_exists(args.target_org, args.target_repo)
        if args.live and exists:
            run(["gh", "repo", "clone", f"{args.target_org}/{args.target_repo}", str(workdir)], ROOT)
            clean_checkout(workdir)
        else:
            workdir.mkdir(parents=True, exist_ok=True)
        copy_source(workdir)
        sanitize(
            workdir,
            args.target_org,
            args.target_repo,
            enable_pages=args.enable_pages,
            include_exports=args.include_exports,
        )
        create_or_confirm_repo(args, dry_run=dry_run)
        if args.enable_pages:
            ensure_pages_enabled(args, dry_run=dry_run)
        git_commit_and_push(workdir, args, dry_run=dry_run, existing_repo=args.live and exists)
    finally:
        if args.keep_workdir:
            print(f"kept deployment workdir: {root_workdir}")
        else:
            shutil.rmtree(root_workdir, ignore_errors=True)


if __name__ == "__main__":
    main()
