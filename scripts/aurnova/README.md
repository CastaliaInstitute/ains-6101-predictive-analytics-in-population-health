# Aurnova Provisioning Scripts

These scripts support the Aurnova cohort and assignment-repo workflow.

## Create A Cohort

Dry run:

```bash
python scripts/aurnova/create_cohort.py \
  --target-org Aurnova \
  --course-code ain6003 \
  --cohort fall2026 \
  --canonical-course-repo Aurnova/ain6003-course \
  --assignment-template-prefix Aurnova/ain6003-assignment-m \
  --module-count 8 \
  --instructor-github-users instructor1,instructor2 \
  --dry-run
```

Live run requires `GH_TOKEN` with permissions to create repos, create teams, and manage members in the target organization.

## Sync Populi Roster

```bash
POPULI_API_BASE=https://school.populiweb.com \
POPULI_API_KEY=... \
python scripts/aurnova/sync_populi_roster.py \
  --course-offering-id 12345 \
  --output-path rosters/current.csv \
  --dry-run
```

The Populi endpoint path should be verified against the tenant before production use.

## Create Student Repos

```bash
python scripts/aurnova/create_student_assignment_repos.py \
  --target-org Aurnova \
  --course-code ain6003 \
  --cohort fall2026 \
  --module 1 \
  --roster-path rosters/current.csv \
  --dry-run
```

Roster CSV columns:

```csv
student_id,name,github_username,email
```

## Deploy Castalia Source To Aurnova

This is the fulfillment step after a customer purchases the course from
`courses.castalia.institute`. The Castalia commerce system should dispatch the
`Fulfill Aurnova Purchase` workflow with an order id; the workflow calls this
script.

Dry run:

```bash
python scripts/aurnova/deploy_to_aurnova.py
```

Live deploy:

```bash
python scripts/aurnova/deploy_to_aurnova.py --live
```

By default this deploys to:

```text
Aurnova/ain6003-instructor
```

The script runs `make site`, copies the source into a temporary deployment tree, removes the Castalia Pages CNAME, rewrites Aurnova workflow defaults to point at `Aurnova/ain6003-instructor`, creates the target repository if needed, commits the sanitized source tree, and pushes it.

It does not configure DNS. Customer DNS, custom domains, and HTTPS policy are handled outside Castalia fulfillment.

It also removes the active Pages deploy workflow by default because private Pages support depends on the customer's GitHub plan. To keep the Pages workflow and attempt to enable workflow-based Pages, run:

```bash
python scripts/aurnova/deploy_to_aurnova.py --live --enable-pages
```

It removes the PDF/EPUB export workflow by default as well. To keep export CI in the Aurnova repo, run:

```bash
python scripts/aurnova/deploy_to_aurnova.py --live --include-exports
```
