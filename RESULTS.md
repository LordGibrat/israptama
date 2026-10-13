# Initial experiment — synthetic data only

These are reproducible simulation results, **not actual savings by an Astana bakery**.

Dataset: 112 days through 2026-10-12; three fictional products; deterministic seed 20261013. Evaluation: 2026-09-22–2026-10-12, 21 days, 63 product-day observations. Default additional stock: 0%.

| Metric | Last-week-sales baseline | Israptama |
|---|---:|---:|
| Forecast WAPE | 8.44% | 7.55% |
| Simulated contribution profit | 1,605,170 ₸ | 1,631,890 ₸ |
| Simulated unsold units | 69 | 85 |
| Simulated unmet demand units | 407 | 314 |

Simulated profit difference: **+26,720 ₸** (about +1.66%). Waste increased by 16 units while unmet demand decreased by 93 units. This result illustrates why reduced forecast error or greater profit does not automatically mean less food waste. Do not claim the prototype already reduced waste.

For 2026-10-13, the initial plan is 63 croissants, 96 bread units, and 79 samsa units: 238 total, 49,120 ₸ variable production cost. These are fictional demonstration recommendations.

The model learns from observed sales, including the effect of historic stockouts. Hidden synthetic demand is used only in evaluation. Price-cost tradeoffs choose the production quantile; residual ranges are descriptive and based on few observations. There is no guarantee that this policy is optimal or transfers to a real bakery.

The next useful evidence is owner feedback and permitted real sales/production records, followed by an actual pilot. A university application should describe the model, baseline, economic assumptions, and findings—including the increase in waste—honestly.
