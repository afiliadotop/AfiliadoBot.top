"""
Modelos Pydantic para produtos
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class Store(str, Enum):
    """Enum de lojas suportadas"""
    SHOPEE = "shopee"
    ALIEXPRESS = "aliexpress"
    AMAZON = "amazon"
    TEMU = "temu"
    SHEIN = "shein"
    MAGALU = "magalu"
    MERCADO_LIVRE = "mercado_livre"

class ProductBase(BaseModel):
    """Modelo base para produtos"""
    store: Store = Field(..., description="Loja do produto")
    name: str = Field(..., min_length=3, max_length=500, description="Nome do produto")
    affiliate_link: str = Field(..., min_length=10, description="Link de afiliado")
    current_price: float = Field(..., gt=0, description="Preço atual")
    
    original_price: Optional[float] = Field(None, gt=0, description="Preço original")
    discount_percentage: Optional[int] = Field(None, ge=0, le=100, description="Porcentagem de desconto")
    
    category: Optional[str] = Field(None, max_length=100, description="Categoria")
    subcategory: Optional[str] = Field(None, max_length=100, description="Subcategoria")
    
    image_url: Optional[str] = Field(None, description="URL da imagem")
    thumbnail_url: Optional[str] = Field(None, description="URL da thumbnail")
    
    rating: Optional[float] = Field(None, ge=0, le=5, description="Avaliação (0-5)")
    review_count: Optional[int] = Field(None, ge=0, description="Número de avaliações")
    
    stock_status: Optional[str] = Field(None, description="Status do estoque")
    shipping_info: Optional[str] = Field(None, description="Informações de frete")
    
    coupon_code: Optional[str] = Field(None, max_length=100, description="Código do cupom")
    coupon_expiry: Optional[datetime] = Field(None, description="Data de expiração do cupom")
    
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags do produto")
    
    source: Optional[str] = Field("manual", description="Fonte do produto")
    source_file: Optional[str] = Field(None, description="Arquivo de origem")
    
    is_active: bool = Field(True, description="Produto ativo")
    is_featured: bool = Field(False, description="Produto em destaque")
    is_trending: bool = Field(False, description="Produto em tendência")
    
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")
    
    @validator('discount_percentage')
    def validate_discount(cls, v, values):
        """Valida que o desconto faz sentido com os preços"""
        if v is not None and 'original_price' in values and values['original_price']:
            calculated_discount = int(((values['original_price'] - values['current_price']) / values['original_price']) * 100)
            if abs(v - calculated_discount) > 5:  # Tolerância de 5%
                raise ValueError(f"Desconto inconsistente. Esperado: {calculated_discount}%, Recebido: {v}%")
        return v
    
    @validator('affiliate_link')
    def validate_affiliate_link(cls, v):
        """Valida que o link é de uma loja suportada"""
        from api.utils.link_processor import detect_store
        store = detect_store(v)
        if not store:
            raise ValueError("Link não reconhecido de nenhuma loja suportada")
        return v

class ProductCreate(ProductBase):
    """Modelo para criação de produto"""
    pass

class ProductUpdate(BaseModel):
    """Modelo para atualização de produto"""
    name: Optional[str] = Field(None, min_length=3, max_length=500)
    current_price: Optional[float] = Field(None, gt=0)
    original_price: Optional[float] = Field(None, gt=0)
    discount_percentage: Optional[int] = Field(None, ge=0, le=100)
    category: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    tags: Optional[List[str]] = None

class ProductInDB(ProductBase):
    """Modelo para produto no banco de dados"""
    id: int = Field(..., description="ID único do produto")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de última atualização")
    last_checked: datetime = Field(..., description="Data da última verificação")
    
    class Config:
        orm_mode = True
        use_enum_values = True
        schema_extra = {
            "example": {
                "id": 1,
                "store": "shopee",
                "name": "Smartphone XYZ 128GB",
                "affiliate_link": "https://shope.ee/ABC123",
                "current_price": 999.90,
                "original_price": 1299.90,
                "discount_percentage": 23,
                "category": "Eletrônicos",
                "image_url": "https://example.com/image.jpg",
                "rating": 4.5,
                "review_count": 1234,
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00",
                "last_checked": "2024-01-01T12:00:00"
            }
        }

# Alias para compatibilidade
Product = ProductInDB
