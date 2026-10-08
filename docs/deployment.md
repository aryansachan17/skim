# Deployment

Skim runs locally for development and on free hosting for **staging**. Production follows the same pattern later.

## How a deploy happens

1. A pull request is merged into `main` (branch protection requires all CI checks to pass first).
2. CI runs again on `main`. When it passes, the **Deploy** workflow (`.github/workflows/deploy.yml`) starts.
3. **Publish backend image:** builds `backend/` once and pushes `ghcr.io/aryansachan17/skim-backend:main-<sha>` (and `latest`). The image is stamped with the commit SHA.
4. **Deploy to staging:** calls the API's Render deploy hook with `imgURL=…:main-<sha>`, so staging runs the exact image CI tested. It then polls `/healthCheck` until it reports `"status":"ok"` **and** `"version":"<sha>"`, and finally deploys the frontend at the same commit.

A deploy is only considered done when the running service reports the new version and healthy dependencies.

## Staging services

| Piece | Where | Plan / region | Notes |
|---|---|---|---|
| API | Render web service `skim-reader-api-staging`, from the existing image `ghcr.io/aryansachan17/skim-backend` | Free, Singapore | Health check path `/livez`. Deploys only come from the pipeline. |
| Frontend | Render static site `skim-reader-web-staging`, from this repo's `main` | Free | Root directory `frontend`, build `corepack pnpm install --frozen-lockfile --prod=false && corepack pnpm build`, publish directory `dist`, auto-deploy off |
| Database | MongoDB Atlas M0 cluster `skim` | Free, AWS Singapore | Database `skim_staging` |
| Redis | Upstash Redis | Free, AWS Singapore | TLS connection (`rediss://`) |

Render's Blueprint (`render.yaml`) and Key Value were not used because they require card verification; standalone free services do not.

## Configuration

### API (Render environment variables)

| Name | Value | Kind |
|---|---|---|
| `SKIM_ENV` | `staging` | plain |
| `SKIM_MONGO_URI` | Atlas connection string for the `skim-app` user | **secret**, entered in Render only |
| `SKIM_REDIS_URL` | Upstash `rediss://` URL | **secret**, entered in Render only |
| `SKIM_CORS_ORIGINS` | `["https://<frontend host>"]` | plain |

Render sets `PORT`; the server reads it. Everything else comes from the `[staging]` section of `backend/settings.toml`.

### Frontend (Render environment variables, used at build time)

| Name | Value |
|---|---|
| `VITE_GRAPHQL_URL` | `https://<api host>/graphql` |
| `COREPACK_ENABLE_DOWNLOAD_PROMPT` | `0` |

Security headers for the static site (Render → Settings → Headers, path `/*`): `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`.

### GitHub `staging` environment

| Name | Kind | Value |
|---|---|---|
| `STAGING_API_DEPLOY_HOOK` | secret | the API's Render deploy hook URL |
| `STAGING_WEB_DEPLOY_HOOK` | secret | the frontend's Render deploy hook URL |
| `STAGING_API_URL` | variable | `https://<api host>` |
| `STAGING_WEB_URL` | variable | `https://<frontend host>` |

If any are missing, the deploy job stops and lists them.

## Database access

- One database user, `skim-app`, with **only** `readWrite` on `skim_staging` and `skim_prod`, restricted to the `skim` cluster. It cannot read other databases or manage users.
- Atlas's IP access list allows `0.0.0.0/0` because Render's free tier has no fixed outbound IP. The generated password and the restricted user are the protection.

## Health checks

| Endpoint | Checks | Used by |
|---|---|---|
| `/livez` | the process answers; never touches MongoDB or Redis | Render's health check (frequent) |
| `/healthCheck` | pings MongoDB and Redis; returns 503 if either is down | the deploy pipeline and humans (once per deploy) |

Keeping frequent checks off the dependencies avoids restart loops when a dependency blips and keeps Redis usage within Upstash's free command limit.

## Free-tier limits

- The staging API sleeps after 15 minutes without traffic; the first request afterwards takes up to a minute.
- Upstash free: 256 MB and 500,000 commands per month.
- Atlas M0: 512 MB storage.

## Re-running a deploy

From the Actions tab, open the failed **Deploy** run and choose **Re-run failed jobs**, or:

```bash
gh run rerun <run-id> --failed --repo aryansachan17/skim
```
