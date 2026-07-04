## Vercel Auto-Deploy Setup

This project is ready to deploy on Vercel as a Next.js app.

Important:
- Automatic updates on Vercel do not come from a local ZIP file.
- They happen when this project is connected to a Git repository and you push changes to the tracked branch.

Recommended setup:
1. Put this folder in a GitHub, GitLab, or Bitbucket repository.
2. Import that repository into Vercel.
3. Keep `main` as the Production Branch.
4. Push new commits to `main` whenever you want the live site to update.

What is already configured in this repo:
- `vercel.json` keeps Git-based deployments enabled for `main`
- `next.config.ts` contains the route rewrites for `/school` and `/uni`
- all current login and dashboard changes are part of the source project

Suggested Vercel settings:
- Framework Preset: `Next.js`
- Root Directory: `./`
- Install Command: `npm install`
- Build Command: `npm run build`
- Output Directory: leave blank

Auto-update flow:
1. Edit the project locally.
2. Commit the changes.
3. Push to `main`.
4. Vercel builds and deploys the new version automatically.

If you want preview deployments before production:
- push to a separate branch first
- Vercel will create a preview deployment for that branch
- merge into `main` when you're happy
