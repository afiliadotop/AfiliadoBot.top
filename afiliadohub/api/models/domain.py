"""
Domain Models - Pydantic models for business entities
ITIL Activity: Design (Domain Definition)
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class Product(BaseModel):
    """Product domain model"""
    id: Optional[int] = None
    name: str = Field(..., min_length=3, max_length=500)
    store: str = Field(..., description="Store name (shopee, mercadolivre, etc)")
    affiliate_link: str = Field(..., min_length=10)
    current_price: float = Field(..., gt=0)
    original_price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    coupon_code: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    active: bool = Field(default=True)
    commission_rate: Optional[float] = Field(None, ge=0, le=100)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Smartphone XYZ",
                "store": "shopee",
                "affiliate_link": "https://shope.ee/abc123",
                "current_price": 1299.90,
                "original_price": 1599.90,
                "category": "electronics",
                "commission_rate": 8.5
            }
        }


class Store(BaseModel):
    """Store domain model"""
    id: Optional[int] = None
    name: str = Field(..., description="Store identifier (shopee, mercadolivre)")
    display_name: str = Field(..., description="Display name")
    api_enabled: bool = Field(default=False)
    commission_default: float = Field(default=0.0, ge=0, le=100)
    created_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "shopee",
                "display_name": "Shopee",
                "api_enabled": True,
                "commission_default": 8.0
            }
        }


class User(BaseModel):
    """User domain model (simplified)"""
    id: Optional[str] = None  # UUID from Supabase Auth
    email: Optional[str] = None
    role: str = Field(default="user", description="User role (admin, user)")
    created_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "role": "user"
            }
        }


class ProductCreate(BaseModel):
    """Model for creating products"""
    name: str = Field(..., min_length=3, max_length=500)
    store: str
    affiliate_link: str = Field(..., min_length=10)
    current_price: float = Field(..., gt=0)
    original_price: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    coupon_code: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    """Model for updating products"""
    name: Optional[str] = Field(None, min_length=3, max_length=500)
    current_price: Optional[float] = Field(None, gt=0)
    original_price: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    coupon_code: Optional[str] = None
    tags: Optional[List[str]] = None
    active: Optional[bool] = None
    commission_rate: Optional[float] = Field(None, ge=0, le=100)


class ProductFilter(BaseModel):
    """Model for filtering products"""
    store: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = Field(None, gt=0)
    max_price: Optional[float] = Field(None, gt=0)
    active: Optional[bool] = True
    min_commission: Optional[float] = Field(None, ge=0, le=100)
    tags: Optional[List[str]] = None
