# AI Harness verification — Israptama

Date: 2026-10-13. Route: normal → plan → implementation → automated tests → independent review → browser verification.

Capabilities materially used: ECC Python patterns (module boundaries, validation, explicit errors); ECC frontend design direction (calm bakery operations dashboard); Superpowers planning and test-driven development (financial, temporal, and CSV contracts); Superpowers requesting code review (independent reviewer); frontend browser loop and verification-before-completion (fresh browser/test evidence).

## Passed

- AI Harness project onboarding and doctor.
- 24 unit/integration tests: financial accounting, stockouts, no future-row leakage, CSV BOM, invalid quantities/prices, duplicate date/product, duplicate headers, oversized fields, gaps, insufficient history, synthetic provenance, buffer effects, localhost HTTP errors and origin rejection.
- Python compilation and JavaScript syntax checks.
- Visible Chrome/Playwright desktop verification: all four views, malformed CSV validation, valid synthetic upload and provenance, sample reset, buffer 0 → 20 → 0, CSV plan download, JSON report download.
- Mobile viewport 390 × 844: no document horizontal overflow; product recommendations visible without horizontal scrolling.
- Final successful page load: no console errors/warnings. The negative upload test intentionally returned HTTP 400 and displayed the validation message.
- Independent review findings fixed: selection bias from dropping sellout calibration days; unhandled CSV field errors; duplicate headers; buffer slider changes while request was pending. Regression tests cover calculation/CSV fixes, and the buffer is disabled during requests and synchronized to the applied result.

## Limitations / checks not applicable

- Real bakery data, customer interviews, and real business savings have not been validated.
- No frontend framework build or package.json exists: production build and project lint/typecheck scripts are not applicable. Python compilation and JavaScript syntax checked instead.
- No public deployment, authentication, or external integrations included.
- This prototype uses observed-sales regression, not a censoring-aware demand model. Results on synthetic data do not prove effectiveness on real data.

## Bakery design refresh — 2026-10-13

Route: normal → reference research → design direction → implementation → review → verify. CodeGraph provided current frontend symbol source. ECC frontend design direction and the browser loop informed layout, original SVG artwork, responsiveness, and accessibility.

References reviewed: Lamanna Bakery via Lapa Ninja (curated full-page image and live homepage), Bernice Bakery via Awwwards. Original vector artwork, system fonts, and local assets preserve offline operation.

Fresh checks passed: all 24 existing tests; Python compilation; JavaScript syntax; desktop app load and all four SVG assets; hero data-upload action; invalid and valid CSV upload; synthetic provenance; sample reset; buffer 0 → 10 → 0; plan/report downloads; all four views at a 390 × 844 mobile viewport without document overflow. Final clean app reload checked separately from the intentional HTTP 400 negative test. No framework build/lint/typecheck script exists; no new runtime dependencies added.

## GitHub preparation — 2026-10-13

Route: small → prepare → test → verify. Prepared an English repository overview, screenshot, upload guide, CV description, development transparency notes, pinned tested NumPy version, ignore rules, and read-only GitHub Actions workflow. Action versions were checked against official action documentation. Local main branch initialized; no commit, remote, push, or public repository created.

The CV records outreach to five Astana bakeries as reported by the owner. It does not claim completed interviews, received private data, or a validated pilot.

The GitHub-ready archive includes only the curated source/assets, synthetic data, tests, and documentation. Tests and syntax checks run in the clean packaged directory. GitHub-hosted CI itself remains unexecuted until upload. No application behavior or UI changes were made in this preparation step, so the previous browser acceptance evidence remains applicable; a new browser regression run was intentionally not repeated.

## Publication — 2026-10-13

Public repository created at https://github.com/LordGibrat/israptama with the owner's authorization. Route: small → inspect prepared files → credential-pattern scan → test → publish → verify remote commit and CI.

ECC GitHub operations guided repository creation and CI readback through gh. Action v7 tag identities were verified against GitHub API and pinned to immutable commit hashes. Only project source/assets, synthetic data, tests, and documentation are published; `.git`, caches, environment files, and private data are excluded.

The local checks are 24 unit/integration tests, Python compilation, and JavaScript syntax. Publication verification checks the remote main commit, repository visibility, file tree, and the first GitHub Actions run. Browser tests are intentionally not repeated because this step changes repository metadata/documentation and workflow pins only.

## Vercel publication — 2026-11-09

Route: complex → inspect application and deployment constraints → adapt shared API and static assets → test and review → publish → verify public deployment. ECC deployment and security guidance, CodeGraph, independent review, and a browser verification loop materially informed this work.

Published the feature-branch version at https://israptama.vercel.app/. Vercel built a Python 3.13 function and served the dashboard and assets publicly. The repository's GitHub integration is not authorized in this Vercel account; the project was deployed from an explicit source-file upload, so future pushes require a new deployment until Git integration is connected. The GitHub PR remains open and unmerged.

Checks passed: 34 Python tests, JavaScript syntax, `vercel.json` JSON parsing, and `git diff --check`. Live requests returned 200 for the dashboard, hero image, research metadata, analysis, review classification, and sample/template CSV downloads. Same-origin hosted POSTs worked and returned `Cache-Control: no-store`; malformed JSON returned 400, foreign or null Origin 403, unsupported media type 415, and oversized review body 413. Source/config URLs (`/engine.py`, `/research/artifacts/results.json`, `/.mcp.json`) returned 404.

Visible browser checks on the public URL covered all five views, review example classification, synthetic CSV upload, buffer 0 → 10 → 0 (quantity 238 → 261 → 238), and 390 px and 320 px mobile layouts without document overflow. The final browser session had zero console errors or warnings and all observed requests completed with 200 status. These checks establish deployment behavior, not real bakery performance or validation on Kazakh reviews.

After adding the public link to the presentation, slide 7 was opened in a browser at 320 px width: its Vercel address and controls were visible without document overflow. The deck loaded with zero console errors or warnings.

## Assignment 2 strict review and live slides — 2026-11-09

Route: complex → read the actual one-page assignment PDF → independent research and demo reviews → fix presentation access and readability → test → redeploy → verify. The PDF contains no point weights or requirement for a GitHub contribution count, so no numeric grade or 100% outcome is predicted. Its remaining administrative action is selecting a presentation slot with the student's ICT Lab Instructor. The open PR and feature branch contain the NLP work; `main` still has the earlier planning app.

The research audit reran `python research/run_experiment.py --check` successfully against the pinned UCI archive and found no definite recipe or exact-text leakage. The expanded candidate's test F1 gain remains uncertain, and the classifier settings are unchanged while the pipeline's text representation changes. [ASSIGNMENT_EVIDENCE.md](ASSIGNMENT_EVIDENCE.md) maps every stated assignment requirement to inspectable evidence and records this interpretation risk.

Presentation fixes: slide 6 makes the 95% interval legible at a 1280 × 720 laptop viewport; slide 7 has prominent live-demo and source links. The deck was moved to `public/presentation.html`, with external CSS and JavaScript so the existing content security policy permits it online. An HTTP regression test checks all three files. Local browser verification saw eight working slides, visible slide-7 links, no horizontal overflow or console errors; the hosted version returned 200 for HTML/CSS/JS and repeated the slide-7 check with no errors. The existing dashboard, research API and analysis API continued to return 200 after redeployment; `/engine.py` remained 404.

Fresh checks passed: 35 Python tests, JavaScript syntax, Git whitespace check, and both GitHub Actions runs on the new feature-branch commit. One intermediate Windows localhost test run saw a connection-aborted error after the server had returned a 403; the complete suite passed on rerun without code changes. The Vercel production deployment reached READY and keeps the same public alias.
