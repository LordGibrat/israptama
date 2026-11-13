# Israptama · Assignment #2 pitch and defense notes

Open the [eight-slide deck](https://israptama.vercel.app/presentation.html) and the [live dashboard](https://israptama.vercel.app/) in separate tabs. The deck is in English; the dashboard controls are in Kazakh. Use the arrow keys, Page Up / Page Down, Space, on-screen controls, or swipe. Press Home to restart. For offline use, keep the entire public/ directory together: the deck needs presentation.html, presentation.css, presentation.js, and its two images in public/assets/. The dashboard can run with python app.py --port 8765 at http://localhost:8765 after installing requirements.txt.

**The proposition:** Israptama helps a baker make two clearer decisions in one dashboard: what quantity to prepare from sales history, and which written feedback deserves a closer look. These are separate signals. The NLP study does not change the production forecast, and neither part has a verified bakery business impact yet.

The eight timings below total **7:00**, followed by **2–3 minutes of questions**. This order sells the owner's problem and shows the product early, then earns trust through the research evidence. Rehearse on the laptop and network you will use in the room. The quotation marks below mark spoken words; bracketed lines are stage directions.

## Seven-minute spoken script

### 1 · The owner's decision · 0:00–0:35

“Imagine closing a small bakery. You know what you baked and sold today, and you have comments from customers. Tomorrow you must decide how much to prepare. You also need to notice feedback that deserves a closer look. Israptama puts these two decisions in one clear workflow. I will show the product first, then the real NLP experiment behind its feedback view, and finally what we still need to prove.”

### 2 · Two signals, two actions · 0:35–1:15

“The first signal is numerical: daily baked and sold counts inform a suggested quantity for tomorrow. Too much stock and a sellout have different costs. The second signal is written: an English review can be flagged for a person's attention when its language resembles reviews with low ratings. The owner remains responsible for the decision. A review is qualitative feedback, not a sales count. I keep it separate from the quantity forecast because a negative sentence does not tell us how many loaves to bake.”

### 3 · The working MVP · 1:15–2:05

“Here is the MVP. The production view turns baked and sold counts into tomorrow's suggested quantity, using simulated data in this demo. Now I open Пікірлер and classify a synthetic English muffin review. The two model outputs and measured comparison appear together. This is a signal for a person to inspect, and it does not alter the production plan.”

[Switch to the prepared dashboard tab; show the plan first, open Пікірлер, classify the example, point to both outputs and the measured comparison, then return to slide 4. Keep the interaction under about 25 seconds.]

### 4 · Open data and an honest test · 2:05–3:20

“For the research component I used UCI's open Recipe Reviews and User Feedback dataset, licensed CC BY 4.0. It contains 18,182 comments. A fixed recipe-title rule and cleaning left 5,984 rated reviews from 38 bakery-like recipes. I predict one-to-three-star ratings versus four or five stars from review text alone. Low rating is a proxy for concerning feedback, not a verified complaint. A random comment split could put reviews of the same recipe on both sides, so I held out entire recipes: 25 recipes and 4,011 reviews for training, six and 799 for validation, and seven unseen recipes with 1,174 reviews for final testing. Only 73 test reviews are low-rated. Exact normalized duplicates were removed before the split. TF-IDF learned from training text only; validation chose the thresholds and live model before the final test. This measures transfer to unseen recipes, though seven test recipes leave uncertainty.”

### 5 · One controlled model change · 3:20–4:10

“Option A asks for a meaningful modification and comparison. My baseline represents each review with word-unigram TF-IDF, normalizes the row, and uses class-weighted logistic regression. The candidate adds character patterns of length three to five to those word features, then uses the same normalization and classifier. The training rows, split, C value, solver, class weighting, and evaluation rule stay fixed. Character patterns might catch spelling variants or word fragments, but they can also add noise. This is a controlled change to the end-to-end feature pipeline; I am not claiming that I invented a new classifier or trained a large language model.”

### 6 · The measured trade-off · 4:10–5:25

“On the 1,174 held-out reviews, the expanded model increased low-rating F1 from 0.493 to 0.511 and average precision from 0.518 to 0.558. It caught 48 of the 73 low-rated reviews rather than 36. The cost was more false alerts: 67 rather than 37, so its precision fell from 0.493 to 0.417. That is a trade-off an owner would have to choose, not a clean win. The F1 difference is about 0.017; a recipe-cluster bootstrap gives a 95% interval from about minus 0.066 to plus 0.080. It includes zero, so I cannot claim a reliable improvement. The live headline uses the word baseline because the predeclared validation F1 rule favored it, 0.620155 versus 0.619355. I did not switch models after seeing the test result.”

### 7 · Prove it in a real bakery · 5:25–6:30

“The result supports a working research prototype, not a claim of bakery impact. The text comes from English home-recipe comments, not retail customers, and the model has not been validated on Kazakh reviews. Seven held-out recipes make the model gap uncertain. The planning results use synthetic sales, so no real bakery waste reduction or profit gain has been measured. The next step is one willing bakery partner. With consent, I would collect enough baked-and-sold history and labelled local feedback. I would evaluate the text model on new products, then compare the planning and review workflows with the owner's current routine. Triage usefulness and planning outcomes should be measured separately. The source, split, model choice, predictions, and limitations are already inspectable.”

### 8 · The closing ask · 6:30–7:00

“Israptama is ready for that honest test. It gives a baker one place to plan tomorrow and notice feedback today. My ask is a small, opt-in pilot with one bakery to learn whether those two clearer decisions help in daily work. Bake with foresight; listen with care. Thank you. I am ready to show the code or answer questions.”

## Demo preparation and fallback

1. Open the slide deck and dashboard in separate tabs before the defense. Have the dashboard on Пісіру жоспары with the simulated sample ready. Check that the review request completes beforehand, then return to the planning view and slide 1. Leave the dashboard tab open for slide 3. Keep a third tab ready at the [source repository](https://github.com/LordGibrat/israptama).
2. On slide 3, show the plan first, switch to Пікірлер, choose **Сын пікір**, classify the synthetic English review, and point to the **two outputs** and **held-out metrics**. The selected example only illustrates the interface; it is not evidence of model accuracy. Do not spend the rest of the talk clicking through the app.
3. If the hosted site fails, use the prepared local app at http://localhost:8765 after starting python app.py --port 8765. If neither live version runs, show the slide's preview and research/artifacts/results.json or saved screenshots. Call a preview or screenshot a preview or screenshot; do not describe it as a live run.
4. If someone asks about the planning model, show its synthetic-data label. Its recorded simulation improved forecast WAPE from 8.44% to 7.55% and simulated contribution profit from 1,605,170 ₸ to 1,631,890 ₸, while unsold units rose from 69 to 85. This is a mixed **simulation** result, not verified savings or waste reduction.

## Two-to-three-minute Q&A

Answer the actual questions asked; do not deliver every answer. Aim for 20–30 seconds per response. Lead with the direct answer, then one piece of evidence and its limit.

| Likely challenge | Answer to practise |
| --- | --- |
| What problem does this solve for a bakery owner? | It brings two daily decisions into view: a quantity suggestion based on sales history, and a signal for an English review the owner enters. I have built that workflow, but customer benefit remains a hypothesis until a real bakery pilot measures it. |
| Why combine planning and review analysis if they do not influence one another? | They are both inputs to an owner's daily review, but they answer different questions. Keeping them separate avoids treating a qualitative review as a numerical demand signal. A future integration would need evidence that it improves decisions. |
| Is this an LLM project? | No. It is an NLP text-classification project under Option A. A transparent TF-IDF and logistic-regression pipeline makes the controlled comparison reproducible and needs no external inference API. |
| Did you really modify the algorithm? | I changed the representation in the end-to-end model pipeline by adding character 3–5-gram TF-IDF while holding the classifier and experiment fixed. If “algorithm” means classifier internals alone, this is a narrower match to that wording; I would state that openly. |
| Are low ratings verified complaints? | No. The dataset has star ratings, not complaint labels. One to three stars form a weak proxy. A mixed three-star review or a critical five-star review can break it, so a person must inspect the text. |
| Why split by recipe? | Reviews of one recipe share topic words. Whole-recipe holdout tests transfer to unseen products. Exact normalized duplicate text was removed before splitting; near-duplicates and repeat authors may remain. |
| Why is the simpler model live when the expanded one looks better on test? | The live-model rule was fixed on validation F1. The word baseline scored 0.620155 versus 0.619355, so it was selected before test inspection. Choosing by the later test score would contaminate final evaluation. |
| Is the expanded model reliably better? | I cannot establish that. It caught 12 more low-rated reviews but produced 30 more false alerts. Its F1 difference was about +0.017, with a recipe-cluster 95% interval from roughly −0.066 to +0.080. |
| Why not headline accuracy? | Only 73 of 1,174 test reviews, about 6.2%, are low-rated. Predicting high rating every time could look accurate while finding none of the target class. I report precision, recall, F1, and average precision for the low-rating class. |
| Is a model score of 0.8 an 80% complaint probability? | No. The score is not calibrated as a probability, and the label is low rating rather than verified complaint. It is a signal for a person to examine. |
| Does it work on Kazakh reviews? | That has not been tested. The interface is in Kazakh, but training and test reviews are English. I would collect consented local-language feedback and evaluate it on a new held-out set before making that claim. |
| Does it reduce waste or increase profit? | The NLP experiment does not measure those outcomes. The separate planning comparison is synthetic and even shows more unsold units alongside higher simulated contribution profit. A real bakery pilot is needed. |
| What evidence says bakeries want this? | Initial outreach to five Astana bakeries has started, but replies and validation are pending. The current evidence is a functioning prototype and a reproducible NLP study, not product-market fit. |
| What would you test next? | With a consenting bakery, obtain enough consecutive baked-and-sold history for the current input requirements, gather labelled real feedback, and predefine a comparison with the current routine. Measure decision usefulness, waste, unmet demand, and time saved separately. |

## Source-code tour if requested

1. review_model.py: fixed bakery-title filter, duplicate handling, recipe-group split, both feature pipelines, and local inference.
2. research/run_experiment.py: pinned UCI download, validation-only threshold/model selection, final test metrics, recipe-cluster bootstrap, and artifact checks.
3. research/artifacts/results.json: exact recipe groups, class counts, thresholds, measured results, and caveats. The test_predictions.csv artifact contains hashes and scores, not review text.
4. app.py and public/: the original planning routes and separate review route, with the dashboard and presentation. Classifying a review does not change production planning.
5. tests/: split, model, HTTP, and forecasting checks. After installing requirements.txt, use python research/run_experiment.py --check and python -m unittest discover -s tests -v to verify the recorded results and application behavior.

Dataset attribution: Ali, A., Matuszewski, S., & Czupyt, J. (2023), *Recipe Reviews and User Feedback*, UCI Machine Learning Repository, [DOI 10.24432/C5FG95](https://doi.org/10.24432/C5FG95), CC BY 4.0.
