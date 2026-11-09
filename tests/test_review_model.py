"""Regression checks for the independent recipe-review experiment."""
import unittest

from review_model import (Review, build_model, clean_text, deduplicate,
                          is_bakery_title, split_reviews)


class ReviewModelTests(unittest.TestCase):
    def test_bakery_filter_is_title_only(self):
        self.assertTrue(is_bakery_title("Best Ever Banana Bread"))
        self.assertTrue(is_bakery_title("Pumpkin Spice Cupcakes"))
        self.assertFalse(is_bakery_title("Cheeseburger Soup"))
        self.assertFalse(is_bakery_title("Skillet Shepherd's Pie"))

    def test_normalization_and_conflicting_duplicate_removal(self):
        self.assertEqual(clean_text("  Great&nbsp; bread!\n"), "Great bread!")
        rows = [
            Review("1", "Great bread!", 0),
            Review("2", "  great&nbsp; BREAD! ", 0),
            Review("3", "Bad texture", 1),
            Review("4", "bad   texture", 0),
        ]
        kept, counts = deduplicate(rows)
        self.assertEqual(len(kept), 1)
        self.assertEqual(kept[0].text, "Great bread!")
        self.assertEqual(counts["conflicting_rows_removed"], 2)
        self.assertEqual(counts["duplicate_rows_removed"], 1)

    def test_recipe_group_split_has_no_recipe_or_text_overlap(self):
        rows = [Review(str(i), f"Review for item {i}", i % 2)
                for i in range(40)]
        first = split_reviews(rows)
        self.assertEqual(first, split_reviews(rows))
        groups = []
        texts = []
        for indices in first.values():
            groups.append({rows[i].recipe_code for i in indices})
            texts.append({rows[i].text.casefold() for i in indices})
        for a in range(3):
            for b in range(a + 1, 3):
                self.assertFalse(groups[a] & groups[b])
                self.assertFalse(texts[a] & texts[b])

    def test_candidate_models_hold_classifier_settings_constant(self):
        baseline = build_model("baseline")
        expanded = build_model("expanded")
        self.assertEqual(baseline[-1].get_params(), expanded[-1].get_params())
        self.assertNotEqual(str(baseline[0]), str(expanded[0]))


if __name__ == "__main__":
    unittest.main()
