# Upload Israptama to GitHub

Repository: https://github.com/LordGibrat/israptama (public).

For future changes, use `git add`, `git commit`, and `git push` from the local project. The instructions below also explain how to recreate the project from an archive.

## Suggested repository details

Name: `israptama`

Description: `AI-assisted bakery production planning prototype with sales forecasting, cost-aware recommendations, and a Kazakh dashboard. Evaluated on synthetic data.`

Topics: `python`, `numpy`, `machine-learning`, `demand-forecasting`, `inventory-management`, `food-waste`, `kazakhstan`, `student-project`.

## Browser upload

1. Sign in to GitHub and create a repository named `israptama`.
2. Choose Public if you want admissions reviewers to access it without an invitation. Leave automatic README/license initialization unchecked because the package includes its README and no license has been selected.
3. Extract the GitHub-ready ZIP. Open the inner `israptama` folder.
4. Choose **uploading an existing file** on an empty repository, or **Add file → Upload files** if that menu is shown. Upload the CONTENTS of the inner folder, not the ZIP or an extra parent folder. `README.md`, `app.py`, and `requirements.txt` must be at the repository root.
5. Include the hidden `.github` directory and `.gitignore`. If your file picker does not show hidden files, use the Git method below instead.
6. Commit the upload. Open the repository home page and confirm that its screenshot renders.
7. Open **Actions** and check the `Tests` workflow. It has been prepared and the equivalent checks pass locally, but no remote run has been performed yet.
8. Add the repository URL to your CV/application once it exists.

## Git upload

For a fresh local copy without commits or a remote, run from the `israptama` directory:

```bash
git status
git add .
git commit -m "Add Israptama bakery planning prototype"
```

Then copy the `git remote add origin ...` command shown on YOUR new GitHub repository's page and run it. Finally:

```bash
git push -u origin main
```

For a ZIP extraction without Git metadata, run `git init -b main` first. If Git asks for your author identity, configure your own name and a GitHub-approved email; the project does not invent these values.

The archive contains source, original assets, synthetic data, tests, and documentation. It excludes `.git`, caches, scratch files, credentials, and private bakery data. No public deployment or real business pilot is included.
