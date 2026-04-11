# theoryinpractice.ca

Single-page website deployed via Cloudflare Pages from this repo. Pushes to `main` auto-deploy within ~30 seconds.

## Files
- `index.html` — the live website
- `setup.html` — onboarding guide for Roti
- `CLAUDE.md` — this file

## Deploying changes

When the user says anything like **"push my changes"**, **"save to git"**, **"deploy"**, **"publish"**, or **"make it live"**, run:

```bash
git add -A && git commit -m "Update site" && git push
```

Then tell the user: "Done — refresh theoryinpractice.ca in about 30 seconds."

If the commit message should be more specific, infer it from the changes made in this session (e.g. "Update homepage headline", "Add contact section").

## Before editing

If the user has been away for a while or mentions collaborators, pull first:

```bash
git pull
```

## Notes
- No build step. Edit HTML directly, push, done.
- Don't create new files unless the user asks.
- Don't refactor or restructure existing HTML beyond what the user requests.
