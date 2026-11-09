# Project notes and development transparency

Israptama is an AI-assisted student prototype for bakery production planning. Implementation, interface design, tests, and documentation were developed with AI coding assistance. The repository provides inspectable source, model assumptions, tests, and reproducible evaluation rather than treating generated output as evidence of business impact.

Initial outreach has been made to five bakeries in Astana, as reported by the project owner. Responses and real-data validation are pending. The production-planning evaluation still uses synthetic sales only. A separate NLP experiment uses real, openly licensed English recipe-review text; those results are not bakery demand evidence. Completed customer interviews, permissions to use real business data, a live pilot, paying customers, and real-world savings are not claimed. Afresh is a public conceptual reference; its proprietary implementation was not used.

The interface is Kazakh and the project documentation is English. The app can run locally or at https://israptama.vercel.app/. Hosted CSV and review requests are processed in Vercel Functions; the app does not persist their contents. The current deployment uses uploaded feature-branch source files and is not Git-linked, so commits do not deploy automatically. A GitHub Pages static site alone cannot run the Python backend.

Suggested next milestone: obtain anonymized daily production/sales data with owner permission, evaluate against the same baseline, and collect feedback on recommendations. Keep private business data outside version control.
