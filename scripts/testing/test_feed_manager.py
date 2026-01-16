
import asyncio
import logging
import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock Environment Variables if needed
os.environ["SUPABASE_URL"] = "https://mock.supabase.co"
os.environ["SUPABASE_KEY"] = "mock_key"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_feed_manager():
    """Test FeedManager daily check logic"""
    try:
        from afiliadohub.api.utils.feed_manager import feed_manager
        
        # Mock Supabase response for active feeds
        mock_feeds = [
            {
                "id": "123",
                "name": "Test Feed",
                "url": "http://test.com/feed.csv",
                "store_id": 1,
                "last_run_at": None, # Should trigger run
                "schedule_cron": "0 0 * * *"
            }
        ]
        
        # Mock supabase client in feed_manager
        feed_manager.supabase.client.table = MagicMock()
        feed_manager.supabase.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = mock_feeds
        
        # Mock _process_single_feed to avoid actual download/processing
        with patch.object(feed_manager, '_process_single_feed', new_callable=MagicMock) as mock_process:
            mock_process.return_value = asyncio.Future()
            mock_process.return_value.set_result(None) # Async mock
            
            logger.info("Running check_daily_feeds...")
            await feed_manager.check_daily_feeds()
            
            # Verify if _process_single_feed was called
            if mock_process.called:
                logger.info("✅ SUCCESS: _process_single_feed was triggered for active feed.")
            else:
                logger.error("❌ FAILURE: _process_single_feed was NOT triggered.")
                
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_feed_manager())
