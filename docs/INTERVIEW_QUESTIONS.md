# Interview questions: GitHub Pages

### 1. What is GitHub Pages?
A free static-site hosting service built into GitHub. It publishes HTML, CSS, JavaScript and other static files from a repository, either from a branch or folder, or from the output of a GitHub Actions workflow, and serves them over HTTPS from `<user>.github.io`.

### 2. Can you host dynamic apps here?
Not server-side ones. There is no backend runtime, database or server-side code. You can run dynamic behaviour in the browser with JavaScript and call external APIs. For a backend, use a separate service (a container platform, serverless functions or a VPS) and keep Pages for the front end. GitHub also does not allow Pages to be used for commercial transactions or SaaS.

### 3. What are the limits of GitHub Pages?
Per GitHub's documentation: published sites may be at most 1 GB; the source repository has a recommended limit of 1 GB; deployments time out after 10 minutes; there is a soft bandwidth limit of 100 GB per month; and a soft limit of 10 builds per hour, which does not apply when you publish with a custom Actions workflow (as this project does). Pages is available for public repositories on the Free plan, and for private ones on paid plans.

### 4. How do you update the website?
Commit and push to the publishing branch. In this project a push to `main` triggers the workflow, which validates, tests and redeploys. Changes go live in about a minute. Using pull requests means the checks run before anything is merged.

### 5. What happens when you delete the repo?
The published site goes offline and the URL returns 404. Everything in the repo, including its history, is gone from GitHub unless you have a clone or fork. Deleted repositories can be restored by the owner for a limited time (see GitHub's docs on restoring a deleted repository). Unpublishing without deleting is done in **Settings → Pages**.

### 6. What is the default file that loads?
`index.html` at the root of the published directory. If a path has no file, Pages serves `404.html` when one exists.

### 7. Can you use a custom domain?
Yes. Set it under **Settings → Pages → Custom domain**, add DNS records (a `CNAME` to `<user>.github.io` for subdomains, or the Pages `A`/`AAAA` records for an apex domain) and enable **Enforce HTTPS**, which uses a free certificate.

### Bonus: why use Actions instead of "deploy from a branch"?
Tests gate the release, the deploy root can be a build output folder such as `site/`, there are no build-rate limits, deployments appear as environments with a URL, and permissions can be scoped to the single job that needs them.
