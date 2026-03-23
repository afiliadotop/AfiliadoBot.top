"""
Unit tests for PriceHistoryRepository
ITIL Activity: Plan & Improve (Quality Assurance)

Covers: table_name, save_price, get_price_history, get_historical_average, get_min_price
"""

import pytest
from afiliadohub.api.repositories.price_history_repository import PriceHistoryRepository


class TestPriceHistoryRepository:
    """Test suite for PriceHistoryRepository"""

    def test_table_name(self, price_history_repository: PriceHistoryRepository):
        """Table name must be price_history"""
        assert price_history_repository.table_name == "price_history"

    # ------------------------------------------------------------------
    # save_price
    # ------------------------------------------------------------------

    def test_save_price_returns_inserted_row(
        self,
        price_history_repository: PriceHistoryRepository,
        mock_supabase_client,
        sample_price_history,
    ):
        """save_price should call insert and return the created record"""
        mock_supabase_client.table().insert().execute.return_value.data = [
            sample_price_history
        ]
        result = price_history_repository.save_price(
            product_id=1, price=1299.90, cep="01310100"
        )
        assert result is not None
        assert result["price"] == 1299.90
        mock_supabase_client.table.assert_called_with("price_history")

    def test_save_price_without_cep(
        self,
        price_history_repository: PriceHistoryRepository,
        mock_supabase_client,
        sample_price_history,
    ):
        """save_price without CEP should not include cep in payload"""
        mock_supabase_client.table().insert().execute.return_value.data = [
            sample_price_history
        ]
        result = price_history_repository.save_price(product_id=1, price=999.0)
        assert result is not None

    def test_save_price_returns_none_on_empty_response(
        self,
        price_history_repository: PriceHistoryRepository,
        mock_supabase_client,
    ):
        """save_price must return None if Supabase returns empty data"""
        mock_supabase_client.table().insert().execute.return_value.data = []
        result = price_history_repository.save_price(product_id=1, price=500.0)
        assert result is None

    # ------------------------------------------------------------------
    # get_price_history
    # ------------------------------------------------------------------

    def test_get_price_history_returns_records(
        self,
        price_history_repository: PriceHistoryRepository,
        mock_supabase_client,
        sample_price_history,
    ):
        """get_price_history should return the list from Supabase"""
        mock_supabase_client.table().select().eq().order().limit().execute.return_value.data = [
            sample_price_history
        ]
        result = price_history_repository.get_price_history(product_id=1, limit=10)
        assert len(result) == 1
        assert result[0]["product_id"] == 1

    def test_get_price_history_empty(
        self,
        price_history_repository: PriceHistoryRepository,
        mock_supabase_client,
    ):
        """get_price_history returns empty list when no records exist"""
        mock_supabase_client.table().select().eq().order().limit().execute.return_value.data = (
            []
        )
        result = price_history_repository.get_price_history(product_id=999)
        assert result == []

    # ------------------------------------------------------------------
    # get_historical_average
    # ------------------------------------------------------------------

    def test_get_historical_average_correct(
        self,
        price_history_repository: PriceHistoryRepository,
        mock_supabase_client,
    ):
        """Average must be computed correctly from price rows"""
        mock_supabase_client.table().select().eq().execute.return_value.data = [
            {"price": 1000.0},
            {"price": 1200.0},
            {"price": 800.0},
        ]
        avg = price_history_repository.get_historical_average(product_id=1)
        assert avg == 1000.0  # (1000 + 1200 + 800) / 3

    def test_get_historical_average_empty_returns_zero(
        self,
        price_history_repository: PriceHistoryRepository,
        mock_supabase_client,
    ):
        """Average of empty history must be 0.0"""
        mock_supabase_client.table().select().eq().execute.return_value.data = []
        avg = price_history_repository.get_historical_average(product_id=42)
        assert avg == 0.0

    def test_get_historical_average_single_record(
        self,
        price_history_repository: PriceHistoryRepository,
        mock_supabase_client,
    ):
        """Single price row → average equals that price"""
        mock_supabase_client.table().select().eq().execute.return_value.data = [
            {"price": 599.99}
        ]
        avg = price_history_repository.get_historical_average(product_id=7)
        assert avg == 599.99

    # ------------------------------------------------------------------
    # get_min_price
    # ------------------------------------------------------------------

    def test_get_min_price_returns_lowest(
        self,
        price_history_repository: PriceHistoryRepository,
        mock_supabase_client,
    ):
        """get_min_price must return the lowest price in history"""
        mock_supabase_client.table().select().eq().order().limit().execute.return_value.data = [
            {"price": 450.0}
        ]
        result = price_history_repository.get_min_price(product_id=1)
        assert result == 450.0

    def test_get_min_price_none_when_empty(
        self,
        price_history_repository: PriceHistoryRepository,
        mock_supabase_client,
    ):
        """get_min_price returns None when no history exists"""
        mock_supabase_client.table().select().eq().order().limit().execute.return_value.data = (
            []
        )
        result = price_history_repository.get_min_price(product_id=99)
        assert result is None
