"""Transparent forecasting and inventory economics for the Israptama prototype."""
from __future__ import annotations

import csv
import io
import math
import random
from collections import defaultdict
from datetime import date, timedelta

import numpy as np

FIELDS = ["date", "product", "baked", "sold", "price", "cost"]


def sample_rows() -> list[dict]:
    """Fixed, reproducible fiction; demand is available ONLY for demo evaluation."""
    rng = random.Random(20261013)
    products = [("Круассан", 58, 650, 260), ("Нан", 92, 400, 160),
                ("Самса", 76, 550, 220)]
    start = date(2026, 10, 13) - timedelta(days=112)
    rows = []
    for day in range(112):
        current = start + timedelta(days=day)
        for name, base, price, cost in products:
            season = [0.88, 0.93, 0.98, 1.02, 1.12, 1.27, 1.15][current.weekday()]
            demand = max(0, round(base * season + day * 0.10 + rng.gauss(0, 5)))
            baked = max(0, round(base * 1.18 + rng.gauss(0, 4)))
            rows.append(dict(date=current, product=name, baked=baked,
                             sold=min(baked, demand), price=float(price),
                             cost=float(cost), demand=demand))
    return rows


def export_csv(rows: list[dict]) -> str:
    """Export only the same observable columns a real bakery can provide."""
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS + ["data_source"])
    writer.writeheader()
    for row in rows:
        writer.writerow({**{key: row[key] for key in FIELDS},
                         "data_source": "SYNTHETIC_DEMO" if "demand" in row
                         else row.get("data_source", "USER_UPLOADED_UNVERIFIED")})
    return stream.getvalue()


def parse_csv(text: str) -> list[dict]:
    if not isinstance(text, str) or len(text.encode("utf-8")) > 2_000_000:
        raise ValueError("CSV файлы 2 МБ-тан аспауы керек.")
    text = text.lstrip("\ufeff")
    first_line = text.splitlines()[0] if text.strip() else ""
    separator = ";" if first_line.count(";") > first_line.count(",") else ","
    reader = csv.DictReader(io.StringIO(text), delimiter=separator, strict=True)
    try:
        columns = reader.fieldnames
        records = list(reader)
    except csv.Error as exc:
        raise ValueError("CSV құрылымы қате немесе бір өріс тым ұзын.") from exc
    if not columns or not set(FIELDS).issubset(columns):
        raise ValueError("Міндетті бағандар: " + ", ".join(FIELDS))
    if len(columns) != len(set(columns)):
        raise ValueError("CSV баған атаулары қайталанбауы керек.")
    rows = []
    for line, raw in enumerate(records, 2):
        if line > 15001:
            raise ValueError("CSV ең көбі 15 000 жолдан тұруы керек.")
        try:
            row = {"date": date.fromisoformat(raw["date"].strip()),
                   "product": raw["product"].strip()}
            if row["date"].isoformat() != raw["date"].strip():
                raise ValueError()
            for field in ("baked", "sold", "price", "cost"):
                value = float(raw[field])
                if not math.isfinite(value) or value < 0:
                    raise ValueError()
                if value > (1_000_000 if field in ("baked", "sold") else 1_000_000_000):
                    raise ValueError()
                if field in ("baked", "sold") and not value.is_integer():
                    raise ValueError()
                row[field] = int(value) if field in ("baked", "sold") else value
            if (not row["product"] or len(row["product"]) > 100
                    or row["sold"] > row["baked"]
                    or row["price"] <= row["cost"] or row["cost"] <= 0):
                raise ValueError()
            if raw.get("data_source", "").strip() == "SYNTHETIC_DEMO":
                row["data_source"] = "SYNTHETIC_DEMO"
        except (ValueError, TypeError, AttributeError, KeyError) as exc:
            raise ValueError(f"{line}-жол: күнді, өнім атауын және сандарды тексеріңіз. "
                             "sold ≤ baked және 0 < cost < price болуы керек.") from exc
        rows.append(row)
    validate_rows(rows, require_history=False)
    return sorted(rows, key=lambda row: (row["date"], row["product"]))


def validate_rows(rows: list[dict], require_history: bool = True) -> dict[str, list[dict]]:
    if not rows:
        raise ValueError("Деректер бос. Үлгі CSV құрылымын пайдаланыңыз.")
    grouped = defaultdict(list)
    seen = set()
    for row in rows:
        key = (row["product"], row["date"])
        if key in seen:
            raise ValueError("Бір өнім мен күнге тек бір жол болуы керек.")
        seen.add(key)
        grouped[row["product"]].append(row)
    if len(grouped) > 20:
        raise ValueError("Прототип бір мезгілде ең көбі 20 өнімді талдайды.")
    end_dates = set()
    for name, history in grouped.items():
        history.sort(key=lambda row: row["date"])
        if require_history and not 77 <= len(history) <= 730:
            raise ValueError(f"{name}: әр өнімге 77–730 күндік тарих қажет.")
        if require_history:
            for left, right in zip(history, history[1:]):
                if (right["date"] - left["date"]).days != 1:
                    raise ValueError(f"{name}: күндер үздіксіз болуы керек; "
                                     "жоқ күндерді нақты нөлдік сатылым болса ғана 0 деп толтырыңыз.")
        end_dates.add(history[-1]["date"])
    if require_history and len(end_dates) != 1:
        raise ValueError("Барлық өнімдердің соңғы күні бірдей болуы керек.")
    return dict(grouped)


def economics(quantity: int, demand: int, price: float, cost: float) -> dict:
    sold = min(quantity, demand)
    return {"sold": sold, "waste": max(quantity - demand, 0),
            "missed": max(demand - quantity, 0),
            "profit": sold * price - quantity * cost}


def features(history: list[dict], target: date, origin: date) -> list[float]:
    prior = [row for row in history if row["date"] < target]
    by_date = {row["date"]: row for row in prior}
    previous_week = by_date.get(target - timedelta(days=7))
    lag = previous_week["sold"] if previous_week else prior[-1]["sold"]
    return [1.0, (target - origin).days / 100, float(lag),
            float(np.mean([r["sold"] for r in prior[-7:]])),
            *[float(target.weekday() == weekday) for weekday in range(1, 7)]]


def forecast(history: list[dict], target: date) -> dict:
    """Ridge mean + held-out residuals. All rows at/after target are excluded."""
    prior = sorted((row for row in history if row["date"] < target),
                   key=lambda row: row["date"])
    if len(prior) < 56:
        raise ValueError("Болжам үшін кемінде 56 өткен күн қажет.")
    origin = prior[0]["date"]
    train, calibration = prior[7:-14], prior[-14:]
    x = np.array([features(prior, r["date"], origin) for r in train])
    y = np.array([r["sold"] for r in train], dtype=float)
    mean, scale = x.mean(axis=0), x.std(axis=0)
    mean[0], scale[0] = 0, 1
    scale[scale == 0] = 1
    z = (x - mean) / scale
    penalty = np.eye(x.shape[1]) * 2.0
    penalty[0, 0] = 0
    coefficients = np.linalg.solve(z.T @ z + penalty, z.T @ y)

    def predict(day: date) -> float:
        vector = (np.array(features(prior, day, origin)) - mean) / scale
        return max(0.0, float(vector @ coefficients))

    # Keep every observed-sales residual: dropping sellouts selects low-demand days.
    # This is not a censoring-aware latent-demand estimator; stockouts remain a limitation.
    residuals = [r["sold"] - predict(r["date"]) for r in calibration]
    point = predict(target)
    return {"point": round(point, 3), "residuals": residuals,
            "lower": max(0, math.floor(point + float(np.quantile(residuals, .1)))),
            "upper": max(0, math.ceil(point + float(np.quantile(residuals, .9))))}


def production_plan(prediction: dict, price: float, cost: float, buffer: int) -> int:
    # No salvage: underage p-c, overage c; critical quantile = (p-c)/p.
    quantile = (price - cost) / price
    adjustment = float(np.quantile(prediction["residuals"], quantile))
    return max(0, math.ceil((prediction["point"] + adjustment) * (1 + buffer / 100)))


def analyze(rows: list[dict], synthetic: bool = False, buffer: int = 0) -> dict:
    if isinstance(buffer, bool) or not isinstance(buffer, int) or not 0 <= buffer <= 20:
        raise ValueError("Қосымша қор 0–20% аралығында болуы керек.")
    grouped = validate_rows(rows)
    final = max(row["date"] for row in rows)
    test_start = final - timedelta(days=20)
    products, evaluations = [], []
    totals = {key: {"profit": 0.0, "waste": 0, "missed": 0,
                    "error": 0.0, "demand": 0} for key in ("baseline", "model")}
    chart = defaultdict(lambda: {"actual": 0, "baseline": 0.0, "model": 0.0})
    stockouts = 0
    for name, history in sorted(grouped.items()):
        next_day = final + timedelta(days=1)
        latest = history[-1]
        prediction = forecast(history, next_day)
        quantity = production_plan(prediction, latest["price"], latest["cost"], buffer)
        products.append({"name": name, "forecast": round(prediction["point"], 1),
                         "lower": prediction["lower"], "upper": prediction["upper"],
                         "quantity": quantity, "price": latest["price"], "cost": latest["cost"],
                         "production_cost": round(quantity * latest["cost"], 2),
                         "last_week": next(r["sold"] for r in history
                                           if r["date"] == next_day - timedelta(days=7))})
        for row in (r for r in history if r["date"] >= test_start):
            target = row["date"]
            prior = [r for r in history if r["date"] < target]
            prediction = forecast(prior, target)
            baseline = next(r["sold"] for r in prior if r["date"] == target - timedelta(days=7))
            plan = production_plan(prediction, prior[-1]["price"], prior[-1]["cost"], buffer)
            demand = row["demand"] if synthetic else row["sold"]
            stockouts += row["sold"] == row["baked"]
            for strategy, units, point in (("baseline", baseline, float(baseline)),
                                           ("model", plan, prediction["point"])):
                outcome = economics(units, demand, row["price"], row["cost"])
                for metric in ("profit", "waste", "missed"):
                    totals[strategy][metric] += outcome[metric]
                totals[strategy]["error"] += abs(point - demand)
                totals[strategy]["demand"] += demand
            chart[target]["actual"] += demand
            chart[target]["baseline"] += baseline
            chart[target]["model"] += prediction["point"]
            evaluations.append({"date": target.isoformat(), "product": name,
                                "actual": demand, "forecast": round(prediction["point"], 2),
                                "recommended": plan, "baseline": baseline})
    metrics = {}
    for strategy, values in totals.items():
        metrics[strategy] = {"profit": round(values["profit"], 2), "waste": values["waste"],
                             "missed": values["missed"],
                             "wape": round(values["error"] / values["demand"] * 100, 2)
                             if values["demand"] else None}
    return {"synthetic": synthetic, "buffer": buffer, "rows": len(rows),
            "days": len({r["date"] for r in rows}), "next_date": next_day.isoformat(),
            "start_date": min(r["date"] for r in rows).isoformat(), "end_date": final.isoformat(),
            "evaluation_start": test_start.isoformat(), "evaluation_days": 21,
            "stockout_rows": stockouts, "evaluation_rows": len(evaluations),
            "profit_delta": round(metrics["model"]["profit"] - metrics["baseline"]["profit"], 2),
            "products": products, "metrics": metrics,
            "chart": [{"date": day.isoformat(), **{k: round(v, 2) for k, v in vals.items()}}
                      for day, vals in sorted(chart.items())],
            "evaluation": evaluations}
