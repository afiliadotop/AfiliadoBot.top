import pytest
from unittest.mock import MagicMock, patch
from afiliadohub.api.utils.supabase_client import SupabaseManager

@pytest.fixture
def mock_supabase_env():
    with patch.dict("os.environ", {"SUPABASE_URL": "http://test.url", "SUPABASE_KEY": "test-key"}):
        yield

@pytest.mark.asyncio
async def test_supabase_singleton(mock_supabase_env):
    with patch("afiliadohub.api.utils.supabase_client.create_client") as mock_create:
        manager1 = SupabaseManager()
        manager2 = SupabaseManager()
        assert manager1 is manager2
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_get_system_summary_optimized(mock_supabase_env):
    with patch("afiliadohub.api.utils.supabase_client.create_client") as mock_create:
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        
        manager = SupabaseManager()
        
        # Mock responses
        mock_count1 = MagicMock()
        mock_count1.count = 100
        
        mock_count2 = MagicMock()
        mock_count2.count = 50
        
        mock_rpc1 = MagicMock()
        mock_rpc1.data = 500
        
        mock_rpc2 = MagicMock()
        mock_rpc2.data = [{"store": "shopee", "count": 10}]
        
        # Setup chain calls
        mock_client.table().select().eq().execute.side_effect = [mock_count1]
        mock_client.table().select().gt().eq().execute.side_effect = [mock_count2]
        mock_client.rpc().execute.side_effect = [mock_rpc1, mock_rpc2]
        
        summary = await manager.get_system_summary()
        
        assert summary["total_products"] == 100
        assert summary["products_with_discount"] == 50
        assert summary["telegram_sends"] == 500
        assert summary["stores"]["shopee"] == 10
