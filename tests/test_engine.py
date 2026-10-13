"""Guard financial accounting, CSV boundaries, and chronological forecasts."""
import unittest
import engine


class EngineTests(unittest.TestCase):
    def test_profit_charges_for_unsold_units(self):
        self.assertEqual(engine.economics(10, 7, 500, 200),
                         {"sold": 7, "waste": 3, "missed": 0, "profit": 1500})

    def test_stockout_counts_unmet_demand(self):
        self.assertEqual(engine.economics(5, 8, 500, 200),
                         {"sold": 5, "waste": 0, "missed": 3, "profit": 1500})

    def test_sample_reproducible_with_three_products(self):
        rows = engine.sample_rows()
        self.assertEqual(rows, engine.sample_rows())
        self.assertEqual(len(rows), 336)
        self.assertEqual(len({r["product"] for r in rows}), 3)
        self.assertTrue(all(r["sold"] <= r["baked"] for r in rows))

    def test_csv_roundtrip_and_bom(self):
        rows = engine.sample_rows()
        parsed = engine.parse_csv("\ufeff" + engine.export_csv(rows))
        self.assertEqual(len(parsed), 336)
        self.assertEqual(parsed[0]["sold"], rows[0]["sold"])

    def test_rejects_missing_column(self):
        with self.assertRaises(ValueError):
            engine.parse_csv("date,product,sold\n2026-10-01,bread,10\n")

    def test_rejects_bad_quantities_and_prices(self):
        header = "date,product,baked,sold,price,cost\n"
        for values in ["-1,0,500,200", "5,8,500,200", "10,7,nan,200",
                       "10,7,500,600", "10.5,7,500,200"]:
            with self.subTest(values=values), self.assertRaises(ValueError):
                engine.parse_csv(header + "2026-10-01,bread," + values)

    def test_duplicate_dates_rejected(self):
        row = "2026-10-01,bread,10,7,500,200\n"
        with self.assertRaises(ValueError):
            engine.parse_csv("date,product,baked,sold,price,cost\n" + row + row)

    def test_missing_day_rejected(self):
        rows = engine.sample_rows()
        rows.pop(3)
        with self.assertRaises(ValueError):
            engine.analyze(rows, synthetic=True)

    def test_short_history_rejected(self):
        with self.assertRaises(ValueError):
            engine.analyze(engine.sample_rows()[:30], synthetic=True)

    def test_forecast_cannot_observe_future_rows(self):
        rows = [r for r in engine.sample_rows() if r["product"] == "Круассан"]
        target = rows[80]["date"]
        before = engine.forecast(rows, target)
        altered = [dict(r, sold=10000) if r["date"] >= target else r for r in rows]
        self.assertEqual(before, engine.forecast(altered, target))

    def test_evaluation_uses_last_21_days_and_finite_results(self):
        result = engine.analyze(engine.sample_rows(), synthetic=True)
        self.assertEqual(result["evaluation_days"], 21)
        self.assertEqual(len(result["products"]), 3)
        self.assertTrue(result["synthetic"])
        self.assertTrue(all(p["quantity"] >= 0 for p in result["products"]))

    def test_real_upload_does_not_use_hidden_demand(self):
        rows = engine.sample_rows()
        first = engine.analyze(rows, synthetic=False)
        changed = [dict(r, demand=1000000) for r in rows]
        self.assertEqual(first, engine.analyze(changed, synthetic=False))

    def test_buffer_increases_recommendations(self):
        rows = engine.sample_rows()
        low = engine.analyze(rows, synthetic=True, buffer=0)
        high = engine.analyze(rows, synthetic=True, buffer=20)
        self.assertTrue(all(b["quantity"] >= a["quantity"]
                            for a, b in zip(low["products"], high["products"])))

    def test_synthetic_export_retains_provenance_after_upload(self):
        text = engine.export_csv(engine.sample_rows())
        parsed = engine.parse_csv(text)
        self.assertTrue(all(r.get("data_source") == "SYNTHETIC_DEMO" for r in parsed))

    def test_rejects_numbers_outside_prototype_limits(self):
        with self.assertRaises(ValueError):
            engine.parse_csv("date,product,baked,sold,price,cost\n"
                             "2026-10-01,bread,10,7,1e300,1e299\n")

    def test_csv_duplicate_headers_rejected(self):
        with self.assertRaises(ValueError):
            engine.parse_csv("date,product,baked,sold,sold,price,cost\n"
                             "2026-10-01,bread,10,999,5,500,200\n")

    def test_large_csv_field_is_validation_error(self):
        with self.assertRaises(ValueError):
            engine.parse_csv("date,product,baked,sold,price,cost\n"
                             "2026-10-01," + "x" * 140000 + ",10,5,500,200\n")

    def test_sellout_flags_do_not_drop_high_sales_from_calibration(self):
        rows = [r for r in engine.sample_rows() if r["product"] == "Круассан"]
        uncensored = [dict(r, baked=r["sold"] + 1) for r in rows]
        self.assertEqual(engine.forecast(rows, rows[-1]["date"]),
                         engine.forecast(uncensored, rows[-1]["date"]))


if __name__ == "__main__":
    unittest.main()
