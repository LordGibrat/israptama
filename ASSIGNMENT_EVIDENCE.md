# Assignment 2 evidence and presentation checklist

This guide points the ICT Lab Instructor to the version of Israptama prepared for Assignment 2. The [open pull request](https://github.com/LordGibrat/israptama/pull/1) and its `feature/nlp-feedback-research` branch contain the NLP work; the repository's default `main` branch still contains the earlier planning prototype. The [live MVP](https://israptama.vercel.app/) runs the feature-branch application. The assignment PDF gives requirements but no weighted scoring rubric, so this guide does not predict a percentage.

| Assignment requirement | Evidence to show | Qualification |
| --- | --- | --- |
| Choose NLP/LLM or computer vision | The **Пікірлер** view classifies English recipe-review text using NLP. | This is NLP, not an LLM or text generator. |
| Option A: use an open-source dataset | [UCI Recipe Reviews and User Feedback](https://archive.ics.uci.edu/dataset/911/recipe+reviews+and+user+feedback+dataset), CC BY 4.0; the download checksum and selection rule are recorded in [NLP_RESEARCH.md](NLP_RESEARCH.md). | The comments describe home recipes, not retail bakery customers. |
| Modify the selected ML algorithm | The baseline pipeline uses word-unigram TF-IDF and logistic regression. The candidate adds a character 3–5-gram TF-IDF branch before the shared normalization and classifier. [review_model.py](review_model.py) defines both pipelines. | This is a controlled **pipeline architecture and representation change**; the logistic-regression algorithm and its hyperparameters are held fixed. An instructor who requires a classifier-specific change may interpret this criterion more narrowly. |
| Compare results and make the work reproducible | [research/run_experiment.py](research/run_experiment.py) freezes a recipe-group train/validation/test split, fits features on training data only, chooses thresholds and the displayed model on validation, and records held-out metrics and predictions in `research/artifacts/`. `--check` retrains and verifies them. | Test F1 is 0.493 versus 0.511, but the recipe-cluster 95% interval for the difference includes zero. The validation rule selected the baseline for the live headline. |
| Show source code and an MVP interface | [Live dashboard](https://israptama.vercel.app/), [source PR](https://github.com/LordGibrat/israptama/pull/1), and [tests](tests/). The NLP view is separate from the bakery quantity forecast. | Planning uses synthetic sales; neither component has a retail bakery pilot. |
| Present for at least seven minutes and answer questions for two to three minutes | Eight-slide [live deck](https://israptama.vercel.app/presentation.html) (offline bundle: `public/presentation.*`) and timed [speaker notes with Q&A](presentation/NOTES.md). | Rehearse the actual spoken timing and browser-tab switch on one laptop. |
| Select a presentation time slot | Use the schedule for your own ICT Lab Instructor. | **Still requires the presenter's action.** No time slot can be inferred from the repository. |

## One laptop demonstration

1. Open the [slide deck](https://israptama.vercel.app/presentation.html) in one tab and the [live dashboard](https://israptama.vercel.app/) in another. Keep the [pull request](https://github.com/LordGibrat/israptama/pull/1) available if asked to show source.
2. On slide 7, open **Пікірлер**, choose the English banana-bread example, run classification, and point to both model outputs and the held-out evaluation. Return to **Пісіру жоспары** to show that the production plan remains separate.
3. If internet access fails, run `python app.py --port 8765` after installing `requirements.txt`, and use `http://localhost:8765`. The deck itself opens offline.
4. For questions about leakage or reproducibility, show [NLP_RESEARCH.md](NLP_RESEARCH.md), `research/artifacts/results.json`, the experiment script, and the green [feature-branch tests](https://github.com/LordGibrat/israptama/actions/workflows/tests.yml?query=branch%3Afeature%2Fnlp-feedback-research).

The assignment PDF says nothing needs to be uploaded to its assignment box. Confirm the presentation slot with the instructor and use the PR link when sharing the source, since `main` has not been merged.
