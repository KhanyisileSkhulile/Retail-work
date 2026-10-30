"""M13-01 tests for the RetailAI chatbot intent catalogue."""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHATBOT_DIR = REPO_ROOT / "python-ai" / "chatbot"
sys.path.insert(0, str(CHATBOT_DIR))

from intents import (  # noqa: E402
    INTENT_CATALOG_VERSION,
    INTENTS,
    SLOT_DEFINITIONS,
    get_intent,
    list_intents,
    validate_catalog,
)


class ChatbotIntentCatalogueTests(unittest.TestCase):
    def test_catalogue_has_expected_version(self):
        self.assertEqual(INTENT_CATALOG_VERSION, "1.0")

    def test_catalogue_contains_all_supported_intents(self):
        expected = {
            "GREETING", "HELP", "INVENTORY_LEVEL", "SALES_SUMMARY",
            "TOP_SELLING_PRODUCTS", "DEMAND_FORECAST",
            "REORDER_RECOMMENDATION", "STOCKOUT_STATUS",
            "SALES_FACTOR_ANALYSIS", "DATA_AVAILABILITY", "UNKNOWN",
        }
        self.assertEqual(set(INTENTS), expected)

    def test_every_intent_has_description_examples_and_guidelines(self):
        for intent in list_intents():
            with self.subTest(intent=intent.name):
                self.assertTrue(intent.description.strip())
                self.assertGreaterEqual(len(intent.examples), 1)
                self.assertGreaterEqual(len(intent.response_guidelines), 1)

    def test_all_slots_are_defined(self):
        for intent in list_intents():
            slots = set(intent.required_slots) | set(intent.optional_slots)
            with self.subTest(intent=intent.name):
                self.assertTrue(slots.issubset(SLOT_DEFINITIONS))

    def test_no_slot_is_both_required_and_optional(self):
        for intent in list_intents():
            with self.subTest(intent=intent.name):
                self.assertFalse(set(intent.required_slots) & set(intent.optional_slots))

    def test_forecast_requires_store_and_product(self):
        intent = get_intent("demand_forecast")
        self.assertEqual(intent.required_slots, ("store_id", "product_id"))

    def test_reorder_is_advisory_and_uses_m12_02_output(self):
        intent = get_intent("REORDER_RECOMMENDATION")
        self.assertIn(
            "python-ai/restocking/outputs/retail_restocking_recommendations_m12_02.csv",
            intent.data_sources,
        )
        self.assertTrue(any("purchase order" in rule.lower() for rule in intent.response_guidelines))

    def test_stockout_intent_distinguishes_observation_from_risk(self):
        intent = get_intent("STOCKOUT_STATUS")
        self.assertTrue(any("observed STOCKOUT" in rule for rule in intent.response_guidelines))
        self.assertTrue(any("STOCKOUT_RISK" in rule for rule in intent.response_guidelines))

    def test_forecast_intent_discloses_holdout_scope(self):
        intent = get_intent("DEMAND_FORECAST")
        self.assertTrue(any("rolling one-step-ahead" in rule for rule in intent.response_guidelines))
        self.assertTrue(any("future dates" in rule for rule in intent.response_guidelines))

    def test_unknown_intent_has_no_data_source_and_prompts_clarification(self):
        intent = get_intent("unknown")
        self.assertEqual(intent.data_sources, ())
        self.assertTrue(intent.clarification_prompt)

    def test_get_intent_is_case_insensitive(self):
        self.assertIs(get_intent("greeting"), get_intent("GREETING"))

    def test_unknown_name_raises_key_error(self):
        with self.assertRaises(KeyError):
            get_intent("NOT_A_RETAILAI_INTENT")

    def test_list_intents_can_exclude_unknown(self):
        names = {intent.name for intent in list_intents(include_unknown=False)}
        self.assertNotIn("UNKNOWN", names)
        self.assertEqual(len(names), len(INTENTS) - 1)

    def test_catalogue_validation_returns_no_errors(self):
        self.assertEqual(validate_catalog(), ())


if __name__ == "__main__":
    unittest.main()
