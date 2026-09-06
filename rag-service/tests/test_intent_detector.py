"""Tests for intent detection.

Verifies all mandatory test cases from the specification.
"""

import sys
import os

# Ensure rag-service root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.models.schemas import Intent
from app.services.intent_detector import (
    detect_intent,
    extract_order_id,
    extract_product_id,
    extract_product_query,
)


# ===================================================================== #
#  Mandatory intent classification tests
# ===================================================================== #
class TestIntentDetection:
    """Verify all mandatory test cases."""

    def test_return_policy_query(self):
        assert detect_intent("What is the return policy?") == Intent.POLICY_QUERY

    def test_footwear_return_window(self):
        assert detect_intent("What is the return window for footwear?") == Intent.POLICY_QUERY

    def test_cancel_after_dispatch(self):
        assert detect_intent("Can I cancel my order after dispatch?") == Intent.POLICY_QUERY

    def test_can_i_return(self):
        assert detect_intent("Can I return a shirt?") == Intent.POLICY_QUERY

    def test_product_location(self):
        assert detect_intent("Where can I find Nike shoes?") == Intent.PRODUCT_LOCATION

    def test_which_aisle(self):
        assert detect_intent("Which aisle has footwear?") == Intent.PRODUCT_LOCATION

    def test_inventory_in_stock(self):
        assert detect_intent("Is Nike Air Max in stock?") == Intent.INVENTORY_QUERY

    def test_do_you_have(self):
        assert detect_intent("Do you have blue shoes?") == Intent.INVENTORY_QUERY

    def test_return_request(self):
        assert detect_intent("I want to return order ORD001.") == Intent.RETURN_REQUEST

    def test_exchange_request(self):
        assert detect_intent("Can I exchange order ORD001 for P002?") == Intent.EXCHANGE_REQUEST

    def test_general_query(self):
        assert detect_intent("Tell me something unrelated.") == Intent.GENERAL_QUERY

    def test_general_fallback(self):
        assert detect_intent("Hello, how are you?") == Intent.GENERAL_QUERY

    def test_damaged_product_policy(self):
        assert detect_intent("What happens if the product is damaged?") == Intent.POLICY_QUERY

    def test_return_conditions(self):
        assert detect_intent("What are the return conditions?") == Intent.POLICY_QUERY

    def test_non_returnable(self):
        assert detect_intent("What products cannot be returned?") == Intent.POLICY_QUERY

    def test_blue_shirt_under_2000(self):
        assert detect_intent("Do you have a blue shirt under ₹2000?") == Intent.INVENTORY_QUERY

    def test_store_info(self):
        assert detect_intent("Tell me about this store.") == Intent.GENERAL_QUERY

    def test_exchange_shirt(self):
        assert detect_intent("Can I exchange this shirt?") == Intent.EXCHANGE_REQUEST

    def test_refund_policy(self):
        assert detect_intent("What is the refund policy?") == Intent.POLICY_QUERY

    def test_cancel_order(self):
        assert detect_intent("Can I cancel my order?") == Intent.POLICY_QUERY


# ===================================================================== #
#  Entity extraction tests
# ===================================================================== #
class TestEntityExtraction:
    def test_extract_order_id(self):
        assert extract_order_id("I want to return order ORD001") == "ORD001"

    def test_extract_order_id_missing(self):
        assert extract_order_id("I want to return my shoes") is None

    def test_extract_product_id(self):
        assert extract_product_id("Exchange P001 for P002") == "P001"

    def test_extract_product_id_missing(self):
        assert extract_product_id("I want to return my order") is None

    def test_extract_product_query(self):
        q = extract_product_query("Do you have blue Nike shoes?")
        assert "blue" in q.lower() or "nike" in q.lower()

    def test_extract_product_query_looking_for(self):
        q = extract_product_query("I'm looking for a red shirt")
        assert "red" in q.lower() or "shirt" in q.lower()
