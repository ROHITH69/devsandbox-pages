# Deployment guide

## One-time setup

1. Create an empty **public** repository named `devsandbox-pages` on GitHub (GitHub Pages is free for public repositories on the Free plan).
2. Push this project to `main`.
3. In the repository go to **Settings → Pages → Build and deployment → Source** and choose **GitHub Actions**.
4. Open the **Actions** tab. The *CI/CD to GitHub Pages* run publishes the site.
5. The live URL is `https://<your-username>.github.io/devsandbox-pages/` and is also shown on the workflow run's `deploy` job.

> The task's mini-guide describes **Deploy from a branch → main → / (root)**. That also works for a plain `index.html` at the repo root. This project uses the Actions source so every release is tested first. The site files live in `site/`, which a branch deployment cannot serve (only `/` or `/docs`).

## Updating the site

```bash
git checkout -b change-hero-copy
# edit site/...
python scripts/validate.py
git commit -am "Update hero copy"
git push -u origin change-hero-copy     # open a PR: validate + container test run
# merge the PR: deploy runs automatically
```

## Rolling back

Revert the bad commit and push. The workflow redeploys the previous content.

```bash
git revert <bad-commit-sha>
git push origin main
```

## Custom domain

1. In **Settings → Pages → Custom domain** enter your domain and save.
2. At your DNS provider add either a `CNAME` record pointing to `<your-username>.github.io` (for `www` or other subdomains) or the GitHub Pages `A` records for an apex domain (the current IPs are listed in GitHub's docs).
3. Wait for DNS to propagate, then tick **Enforce HTTPS**.

With the Actions source, the domain is stored in the Pages settings, so you do not need a `CNAME` file.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| 404 on the live URL right after the first run | Check **Settings → Pages** shows *GitHub Actions* as the source and that the `deploy` job finished |
| `deploy` job fails with a permissions error | **Settings → Actions → General → Workflow permissions**: leave on default; the workflow requests `pages: write` itself |
| CSS missing on the live site | Paths in `site/` must be relative (`assets/css/style.css`), not `/assets/...`, because project sites live under `/<repo>/` |
| `validate` fails on the placeholder | Run `python scripts/configure.py --user <you>` (CI does this automatically) |
