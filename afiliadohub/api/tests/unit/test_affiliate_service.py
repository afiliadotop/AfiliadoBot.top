"""
Unit tests for AffiliateService
ITIL Activity: Plan & Improve (Quality Assurance)

Covers: generate_affiliate_link, detect_fake_discount
"""

import pytest
from afiliadohub.api.services.affiliate_service import AffiliateService
from afiliadohub.api.models.domain import AffiliateLinkResult, DiscountAnalysis


class TestAffiliateLinkGeneration:
    """Tests for generate_affiliate_link (skill_generate_affiliate_link)"""

    def test_amazon_tag_injected(self, affiliate_service: AffiliateService):
        """Amazon: tag=afiliadotop-20 must appear in the URL"""
        result = affiliate_service.generate_affiliate_link(
            base_url="https://www.amazon.com.br/dp/B09XYZ123",
            store_name="Amazon",
            offer_id="test-001",
        )
        assert isinstance(result, AffiliateLinkResult)
        assert "tag=afiliadotop-20" in result.monetized_product_url
        assert result.offer_id == "test-001"
        assert result.store_name == "Amazon"

    def test_shopee_tag_injected(self, affiliate_service: AffiliateService):
        """Shopee: af_siteid param must be present"""
        result = affiliate_service.generate_affiliate_link(
            base_url="https://shopee.com.br/product/123",
            store_name="Shopee",
            offer_id="shop-007",
        )
        assert "af_siteid=" in result.monetized_product_url
        assert result.internal_click_url.endswith("/shop-007")

    def test_mercado_livre_tag_injected(self, affiliate_service: AffiliateService):
        """Mercado Livre: afiliado param must be present"""
        result = affiliate_service.generate_affiliate_link(
            base_url="https://www.mercadolivre.com.br/p/MLB123456",
            store_name="Mercado Livre",
            offer_id="ml-100",
        )
        assert "afiliado=" in result.monetized_product_url

    def test_generic_store_fallback(self, affiliate_service: AffiliateService):
        """Unknown store: ref=afiliadotop fallback param"""
        result = affiliate_service.generate_affiliate_link(
            base_url="https://www.americanas.com.br/produto/123",
            store_name="Americanas",
            offer_id="ame-001",
        )
        assert "ref=afiliadotop" in result.monetized_product_url

    def test_internal_click_url_format(self, affiliate_service: AffiliateService):
        """Internal URL must follow the /go/{offer_id} pattern"""
        result = affiliate_service.generate_affiliate_link(
            base_url="https://www.amazon.com.br/dp/B0ABC",
            store_name="Amazon",
            offer_id="promo-42",
        )
        assert "/go/promo-42" in result.internal_click_url

    def test_existing_query_params_preserved(self, affiliate_service: AffiliateService):
        """Existing URL query params must not be wiped"""
        result = affiliate_service.generate_affiliate_link(
            base_url="https://www.amazon.com.br/dp/B0ABC?color=red",
            store_name="Amazon",
            offer_id="color-01",
        )
        assert "color=red" in result.monetized_product_url
        assert "tag=afiliadotop-20" in result.monetized_product_url

    def test_store_name_case_insensitive(self, affiliate_service: AffiliateService):
        """Store name matching must be case-insensitive"""
        result_upper = affiliate_service.generate_affiliate_link(
            base_url="https://www.amazon.com.br/dp/X1",
            store_name="AMAZON",
            offer_id="x1",
        )
        result_lower = affiliate_service.generate_affiliate_link(
            base_url="https://www.amazon.com.br/dp/X1",
            store_name="amazon",
            offer_id="x1",
        )
        assert result_upper.monetized_product_url == result_lower.monetized_product_url


class TestFakeDiscountDetection:
    """Tests for detect_fake_discount (skill_detect_fake_discount)"""

    def test_fake_discount_detected_when_price_inflated(
        self, affiliate_service: AffiliateService
    ):
        """Declared price 30% above average → is_fake_discount=True"""
        result = affiliate_service.detect_fake_discount(
            current_price=500.0,
            declared_from_price=1300.0,  # 30% above average of 1000
            historical_average_price=1000.0,
        )
        assert isinstance(result, DiscountAnalysis)
        assert result.is_fake_discount is True
        assert result.adjusted_from_price == 1000.0  # capped at historical avg

    def test_real_discount_within_threshold(self, affiliate_service: AffiliateService):
        """Declared price only 5% above avg → is_fake_discount=False"""
        result = affiliate_service.detect_fake_discount(
            current_price=900.0,
            declared_from_price=1050.0,  # 5% above avg of 1000
            historical_average_price=1000.0,
        )
        assert result.is_fake_discount is False
        assert result.adjusted_from_price == 1050.0  # not corrected

    def test_real_discount_percentage_correct(
        self, affiliate_service: AffiliateService
    ):
        """Verify the real discount % is computed against adjusted price"""
        result = affiliate_service.detect_fake_discount(
            current_price=800.0,
            declared_from_price=2000.0,  # fake — avg is 1000
            historical_average_price=1000.0,
        )
        # Real discount = (1000 - 800) / 1000 * 100 = 20%
        assert result.real_discount_percentage == 20.0

    def test_zero_historical_average_no_correction(
        self, affiliate_service: AffiliateService
    ):
        """When historical_average=0 (no history), is_fake_discount must be False"""
        result = affiliate_service.detect_fake_discount(
            current_price=500.0,
            declared_from_price=9999.0,
            historical_average_price=0.0,
        )
        assert result.is_fake_discount is False

    def test_no_discount_when_current_equals_original(
        self, affiliate_service: AffiliateService
    ):
        """current_price == original_price → 0% discount"""
        result = affiliate_service.detect_fake_discount(
            current_price=100.0,
            declared_from_price=100.0,
            historical_average_price=100.0,
        )
        assert result.real_discount_percentage == 0.0

    def test_all_fields_populated(self, affiliate_service: AffiliateService):
        """DiscountAnalysis must always return all required fields"""
        result = affiliate_service.detect_fake_discount(
            current_price=750.0,
            declared_from_price=1000.0,
            historical_average_price=950.0,
        )
        assert result.current_price == 750.0
        assert result.declared_from_price == 1000.0
        assert result.historical_average_price == 950.0
        assert isinstance(result.real_discount_percentage, float)
