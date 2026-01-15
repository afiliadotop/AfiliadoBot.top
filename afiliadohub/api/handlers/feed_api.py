from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, List, Optional
from pydantic import BaseModel
import logging
from datetime import datetime

from ..utils.supabase_client import get_supabase_manager
from .auth import get_current_admin
from .csv_import import import_shopee_daily_csv

router = APIRouter(prefix="/feeds", tags=["feeds"])
logger = logging.getLogger(__name__)

# Models
class FeedBase(BaseModel):
    name: str
    url: str
    store_id: int
    schedule_cron: str = "0 0 * * *"

class FeedCreate(FeedBase):
    pass

class FeedUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    is_active: Optional[bool] = None
    schedule_cron: Optional[str] = None

class FeedResponse(FeedBase):
    id: str
    is_active: bool
    last_run_at: Optional[datetime]
    status: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Endpoints ---

@router.get("", response_model=List[feedResponse] if False else List[Dict]) # Simplified return type for flexibility
async def list_feeds(current_admin: Dict = Depends(get_current_admin)):
    """List all product feeds"""
    try:
        manager = get_supabase_manager()
        client = manager.get_authenticated_client(current_admin["token"])
        result = client.table("product_feeds").select("*").order("created_at", desc=True).execute()
        return result.data
    except Exception as e:
        logger.error(f"[Feeds] Error listing feeds: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=Dict)
async def create_feed(feed: FeedCreate, current_admin: Dict = Depends(get_current_admin)):
    """Create a new product feed"""
    try:
        manager = get_supabase_manager()
        client = manager.get_authenticated_client(current_admin["token"])
        data = feed.dict()
        data["updated_at"] = datetime.utcnow().isoformat()
        
        result = client.table("product_feeds").insert(data).execute()
        
        if result.data:
            return result.data[0]
        else:
            raise HTTPException(status_code=400, detail="Failed to create feed")
            
    except Exception as e:
        logger.error(f"[Feeds] Error creating feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{feed_id}/run")
async def run_feed(feed_id: str, background_tasks: BackgroundTasks, current_admin: Dict = Depends(get_current_admin)):
    """Trigger a manual run for a specific feed"""
    try:
        manager = get_supabase_manager()
        client = manager.get_authenticated_client(current_admin["token"])
        
        # Get feed details
        feed = client.table("product_feeds").select("*").eq("id", feed_id).single().execute()
        
        if not feed.data:
            raise HTTPException(status_code=404, detail="Feed not found")
            
        feed_data = feed.data
        
        # Update status to running
        client.table("product_feeds").update({
            "status": "running",
            "last_run_at": datetime.utcnow().isoformat()
        }).eq("id", feed_id).execute()
        
        # Helper function for background task to update status on completion
        async def run_import_task(url: str, fid: str, name: str, token: str):
            logger.info(f"🚀 Starting manual feed import: {name} ({fid})")
            try:
                stats = await import_shopee_daily_csv(url, token=token)
                
                status = "success" if stats and stats.get('errors', 0) == 0 else "warning" if stats else "failed"
                
                # Update final status
                manager_bg = get_supabase_manager()
                client_bg = manager_bg.get_authenticated_client(token)
                
                client_bg.table("product_feeds").update({
                    "status": status,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", fid).execute()
                
                logger.info(f"✅ Manual feed import finished: {name} - {status}")
                
            except Exception as e:
                logger.error(f"❌ Manual feed import failed: {name} - {e}")
                manager_bg = get_supabase_manager()
                try:
                    client_bg = manager_bg.get_authenticated_client(token)
                    client_bg.table("product_feeds").update({
                        "status": "failed",
                        "updated_at": datetime.utcnow().isoformat()
                    }).eq("id", fid).execute()
                except:
                    pass

        # Add to background tasks
        background_tasks.add_task(run_import_task, feed_data["url"], feed_id, feed_data["name"], current_admin["token"])
        
        return {"message": "Feed execution started", "feed_id": feed_id}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Feeds] Error triggering run: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{feed_id}")
async def delete_feed(feed_id: str, current_admin: Dict = Depends(get_current_admin)):
    """Delete a feed"""
    try:
        manager = get_supabase_manager()
        client = manager.get_authenticated_client(current_admin["token"])
        client.table("product_feeds").delete().eq("id", feed_id).execute()
        return {"message": "Feed deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
