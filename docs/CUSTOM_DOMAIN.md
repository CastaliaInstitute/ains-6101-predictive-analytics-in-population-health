# Custom domain: `ains6101.courses.castalia.institute`

Course sites use **`{courseId}.courses.castalia.institute`** so DNS sits on the Castalia zone behind Cloudflare.

## DNS

| Type | Name | Target | Proxy |
|------|------|--------|-------|
| CNAME | `ains6101.courses` | `castaliainstitute.github.io` | Proxied |

Apply locally:

```bash
set -a && source ../castalia.institute/.env && set +a
./scripts/cf-dns-ains6101-github-pages.sh
```

## GitHub Pages

```bash
gh api -X PUT repos/CastaliaInstitute/ains-6101-predictive-analytics-in-population-health/pages \
  -f build_type=workflow \
  -f cname='ains6101.courses.castalia.institute'
```

## Public URL

https://ains6101.courses.castalia.institute/
