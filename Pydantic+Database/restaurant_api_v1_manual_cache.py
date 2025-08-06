"""
Restaurant Management API - Version 1: Basic Redis Caching
FastAPI application with manual Redis caching for performance optimization.

Features:
- Restaurant management with CRUD operations
- Manual Redis caching with namespace-based strategy
- Cache invalidation rules
- Performance monitoring with timing logs
- Cache management endpoints
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum
from typing import List, Optional, Dict, Any
from decimal import Decimal
import re
import time
import redis.asyncio as redis
import logging
from datetime import datetime
import asyncio
import json
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enum for food categories
class FoodCategory(str, Enum):
    APPETIZER = "appetizer"
    MAIN_COURSE = "main_course"
    DESSERT = "dessert"
    BEVERAGE = "beverage"
    SALAD = "salad"

# Pydantic model for Restaurant with comprehensive validations
class Restaurant(BaseModel):
    id: Optional[int] = None  # Auto-generated
    name: str = Field(..., min_length=3, max_length=100, description="Restaurant name")
    description: str = Field(..., min_length=10, max_length=500, description="Restaurant description")
    cuisine_type: FoodCategory = Field(..., description="Cuisine category")
    price_range: Decimal = Field(..., ge=1.00, le=100.00, description="Average price in USD")
    is_active: bool = Field(default=True, description="Active status")
    preparation_time: int = Field(..., ge=1, le=120, description="Average preparation time in minutes")
    specialties: List[str] = Field(..., description="List of specialties")
    rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Rating out of 5")
    is_vegetarian_friendly: bool = Field(default=False, description="Vegetarian friendly")
    is_spicy: bool = Field(default=False, description="Serves spicy food")

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate that name contains only letters and spaces"""
        if not re.match(r'^[a-zA-Z\s]+$', v):
            raise ValueError('Name must contain only letters and spaces')
        return v.strip()

    @field_validator('specialties')
    @classmethod
    def validate_specialties(cls, v):
        """Validate specialties list"""
        if not v:
            raise ValueError('At least one specialty is required')
        return [specialty.strip() for specialty in v if specialty.strip()]

    @model_validator(mode='after')
    def validate_business_rules(self):
        """Custom validation rules based on category and properties"""
        cuisine_type = self.cuisine_type
        is_spicy = self.is_spicy
        preparation_time = self.preparation_time
        is_vegetarian_friendly = self.is_vegetarian_friendly
        rating = self.rating

        # Rule 1: Desserts and beverages cannot be primarily spicy
        if cuisine_type in [FoodCategory.DESSERT, FoodCategory.BEVERAGE] and is_spicy:
            raise ValueError(f'{cuisine_type.value} establishments cannot be primarily spicy')

        # Rule 2: Beverages must have prep time ≤ 10 minutes
        if cuisine_type == FoodCategory.BEVERAGE and preparation_time > 10:
            raise ValueError('Beverage establishments must have preparation time of 10 minutes or less')

        # Rule 3: Vegetarian friendly establishments with rating should have rating >= 3.0
        if is_vegetarian_friendly and rating is not None and rating < 3.0:
            raise ValueError('Vegetarian friendly establishments should maintain rating >= 3.0')

        return self

    @property
    def price_category(self) -> str:
        """Computed property for price category"""
        if self.price_range < 10:
            return "Budget"
        elif self.price_range <= 25:
            return "Mid-range"
        else:
            return "Premium"

    @property
    def service_info(self) -> List[str]:
        """Computed property for service information tags"""
        tags = []
        if self.is_vegetarian_friendly:
            tags.append("Vegetarian Friendly")
        if self.is_spicy:
            tags.append("Spicy Options")
        if self.rating and self.rating >= 4.0:
            tags.append("Highly Rated")
        if self.preparation_time <= 15:
            tags.append("Quick Service")
        return tags

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with computed properties"""
        data = self.model_dump()
        data['price_category'] = self.price_category
        data['service_info'] = self.service_info
        return data

# Request models for API
class RestaurantCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    cuisine_type: FoodCategory
    price_range: Decimal = Field(..., ge=1.00, le=100.00)
    is_active: bool = Field(default=True)
    preparation_time: int = Field(..., ge=1, le=120)
    specialties: List[str] = Field(...)
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    is_vegetarian_friendly: bool = Field(default=False)
    is_spicy: bool = Field(default=False)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z\s]+$', v):
            raise ValueError('Name must contain only letters and spaces')
        return v.strip()

    @field_validator('specialties')
    @classmethod
    def validate_specialties(cls, v):
        if not v:
            raise ValueError('At least one specialty is required')
        return [specialty.strip() for specialty in v if specialty.strip()]

    @model_validator(mode='after')
    def validate_business_rules(self):
        cuisine_type = self.cuisine_type
        is_spicy = self.is_spicy
        preparation_time = self.preparation_time
        is_vegetarian_friendly = self.is_vegetarian_friendly
        rating = self.rating

        if cuisine_type in [FoodCategory.DESSERT, FoodCategory.BEVERAGE] and is_spicy:
            raise ValueError(f'{cuisine_type.value} establishments cannot be primarily spicy')

        if cuisine_type == FoodCategory.BEVERAGE and preparation_time > 10:
            raise ValueError('Beverage establishments must have preparation time of 10 minutes or less')

        if is_vegetarian_friendly and rating is not None and rating < 3.0:
            raise ValueError('Vegetarian friendly establishments should maintain rating >= 3.0')

        return self

class RestaurantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    cuisine_type: Optional[FoodCategory] = None
    price_range: Optional[Decimal] = Field(None, ge=1.00, le=100.00)
    is_active: Optional[bool] = None
    preparation_time: Optional[int] = Field(None, ge=1, le=120)
    specialties: Optional[List[str]] = Field(None)
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    is_vegetarian_friendly: Optional[bool] = None
    is_spicy: Optional[bool] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not re.match(r'^[a-zA-Z\s]+$', v):
            raise ValueError('Name must contain only letters and spaces')
        return v.strip() if v else v

    @field_validator('specialties')
    @classmethod
    def validate_specialties(cls, v):
        if v is not None:
            if not v:
                raise ValueError('At least one specialty is required')
            return [specialty.strip() for specialty in v if specialty.strip()]
        return v

# Response models
class CacheStats(BaseModel):
    """Cache statistics model"""
    total_keys: int
    namespace_breakdown: Dict[str, int]
    redis_info: Dict[str, Any]

# ===== IN-MEMORY DATABASE =====
restaurants_db: Dict[int, Restaurant] = {}
next_restaurant_id = 1

def get_next_restaurant_id() -> int:
    global next_restaurant_id
    current_id = next_restaurant_id
    next_restaurant_id += 1
    return current_id

# ===== REDIS CONFIGURATION =====
redis_client = None

async def get_redis_client():
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(
            host="localhost",
            port=6379,
            db=0,
            decode_responses=True
        )
    return redis_client

# ===== CACHE UTILITIES =====
class CacheManager:
    """Manage Redis caching operations"""
    
    @staticmethod
    async def get_cache_key(namespace: str, key: str) -> str:
        """Generate cache key with namespace"""
        return f"restaurant-cache:{namespace}:{key}"
    
    @staticmethod
    async def get_cached_data(namespace: str, key: str):
        """Get data from cache"""
        redis_conn = await get_redis_client()
        cache_key = await CacheManager.get_cache_key(namespace, key)
        
        try:
            cached_data = await redis_conn.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    @staticmethod
    async def set_cached_data(namespace: str, key: str, data: Any, ttl: int = 300):
        """Set data in cache with TTL"""
        redis_conn = await get_redis_client()
        cache_key = await CacheManager.get_cache_key(namespace, key)
        
        try:
            serialized_data = json.dumps(data, default=str)
            await redis_conn.setex(cache_key, ttl, serialized_data)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    @staticmethod
    async def clear_namespace(namespace: str):
        """Clear all keys in a namespace"""
        redis_conn = await get_redis_client()
        pattern = f"restaurant-cache:{namespace}:*"
        
        try:
            keys = await redis_conn.keys(pattern)
            if keys:
                await redis_conn.delete(*keys)
                logger.info(f"🗑️ Cleared {len(keys)} keys from namespace '{namespace}'")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
    
    @staticmethod
    async def clear_all_cache():
        """Clear all cache data"""
        redis_conn = await get_redis_client()
        pattern = "restaurant-cache:*"
        
        try:
            keys = await redis_conn.keys(pattern)
            if keys:
                await redis_conn.delete(*keys)
                logger.info(f"🗑️ Cleared {len(keys)} total cache keys")
                return len(keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear all error: {e}")
            return 0

# ===== LIFESPAN MANAGEMENT =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    try:
        redis_conn = redis.Redis(
            host="localhost",
            port=6379,
            db=0,
            decode_responses=True
        )
        
        # Test Redis connection
        await redis_conn.ping()
        logger.info("✅ Connected to Redis successfully")
        
        # Seed sample data
        seed_sample_restaurants()
        logger.info("✅ Sample restaurants data seeded")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Redis: {e}")
        raise
    finally:
        # Shutdown
        global redis_client
        if redis_client:
            await redis_client.close()
            logger.info("✅ Redis connection closed")

# ===== FASTAPI APP INITIALIZATION =====
app = FastAPI(
    title="Restaurant Management API - Version 1 (Redis Cache)",
    description="Restaurant management system with Redis caching for performance optimization",
    version="1.0.0",
    lifespan=lifespan
)

# ===== SAMPLE DATA SEEDING =====
def seed_sample_restaurants():
    """Populate the database with sample restaurants"""
    sample_restaurants = [
        {
            "name": "Bella Italia",
            "description": "Authentic Italian cuisine with fresh pasta, wood-fired pizzas, and traditional recipes passed down through generations",
            "cuisine_type": FoodCategory.MAIN_COURSE,
            "price_range": Decimal("18.99"),
            "preparation_time": 25,
            "specialties": ["Margherita Pizza", "Carbonara Pasta", "Tiramisu", "Bruschetta"],
            "rating": 4.5,
            "is_vegetarian_friendly": True,
            "is_spicy": False
        },
        {
            "name": "Spice Kingdom",
            "description": "Fiery Indian and Thai dishes with aromatic spices, curries, and traditional cooking methods for the bold palate",
            "cuisine_type": FoodCategory.MAIN_COURSE,
            "price_range": Decimal("15.50"),
            "preparation_time": 20,
            "specialties": ["Chicken Tikka Masala", "Pad Thai", "Vindaloo", "Samosas"],
            "rating": 4.2,
            "is_vegetarian_friendly": True,
            "is_spicy": True
        },
        {
            "name": "Garden Fresh Salads",
            "description": "Healthy and nutritious salad bar with organic ingredients, custom dressings, and superfood toppings",
            "cuisine_type": FoodCategory.SALAD,
            "price_range": Decimal("12.00"),
            "preparation_time": 8,
            "specialties": ["Caesar Supreme", "Mediterranean Bowl", "Quinoa Power", "Asian Fusion"],
            "rating": 4.0,
            "is_vegetarian_friendly": True,
            "is_spicy": False
        },
        {
            "name": "Sweet Dreams Desserts",
            "description": "Artisanal desserts and pastries made fresh daily with premium ingredients and creative presentations",
            "cuisine_type": FoodCategory.DESSERT,
            "price_range": Decimal("8.75"),
            "preparation_time": 15,
            "specialties": ["Chocolate Lava Cake", "New York Cheesecake", "French Macarons", "Gelato"],
            "rating": 4.7,
            "is_vegetarian_friendly": True,
            "is_spicy": False
        },
        {
            "name": "Fresh Juice Bar",
            "description": "Cold-pressed juices, smoothies, and healthy beverages made from organic fruits and vegetables",
            "cuisine_type": FoodCategory.BEVERAGE,
            "price_range": Decimal("6.50"),
            "preparation_time": 5,
            "specialties": ["Green Detox", "Tropical Smoothie", "Fresh OJ", "Protein Shake"],
            "rating": 4.3,
            "is_vegetarian_friendly": True,
            "is_spicy": False
        }
    ]
    
    global restaurants_db, next_restaurant_id
    for restaurant_data in sample_restaurants:
        restaurant_id = get_next_restaurant_id()
        restaurant = Restaurant(id=restaurant_id, **restaurant_data)
        restaurants_db[restaurant_id] = restaurant

# ===== UTILITY FUNCTIONS =====
def log_performance(cache_status: str, start_time: float, endpoint: str):
    """Log performance metrics"""
    duration = (time.time() - start_time) * 1000
    logger.info(f"🔍 {endpoint} | Cache: {cache_status} | Time: {duration:.2f}ms")
    return duration

async def clear_restaurant_cache():
    """Clear all restaurant-related caches"""
    try:
        await CacheManager.clear_namespace("restaurants")
        await CacheManager.clear_namespace("search")
    except Exception as e:
        logger.error(f"❌ Failed to clear cache: {e}")

# ===== CORE API ENDPOINTS WITH CACHING =====

@app.get("/")
async def root():
    """Root endpoint with API information"""
    start_time = time.time()
    result = {
        "message": "Restaurant Management API - Version 1 (Redis Cache)",
        "version": "1.0.0",
        "features": ["Redis Caching", "Performance Monitoring", "Cache Management"],
        "endpoints": {
            "restaurants": "/restaurants",
            "cache": "/cache",
            "docs": "/docs"
        }
    }
    duration = log_performance("BYPASS", start_time, "GET /")
    result["cache_status"] = "BYPASS"
    result["response_time_ms"] = duration
    return result

@app.get("/restaurants")
async def get_all_restaurants():
    """Get all restaurants with caching (TTL: 300 seconds)"""
    start_time = time.time()
    cache_key = "all_restaurants"
    
    # Try to get from cache first
    cached_data = await CacheManager.get_cached_data("restaurants", cache_key)
    
    if cached_data:
        duration = log_performance("HIT", start_time, "GET /restaurants")
        cached_data["cache_status"] = "HIT"
        cached_data["response_time_ms"] = duration
        return cached_data
    
    # Cache miss - get from database
    await asyncio.sleep(0.1)  # Simulate processing time
    
    restaurants_data = [restaurant.to_dict() for restaurant in restaurants_db.values()]
    duration = log_performance("MISS", start_time, "GET /restaurants")
    
    result = {
        "data": restaurants_data,
        "cache_status": "MISS",
        "response_time_ms": duration,
        "total_count": len(restaurants_data)
    }
    
    # Store in cache
    await CacheManager.set_cached_data("restaurants", cache_key, result, ttl=300)
    
    return result

@app.get("/restaurants/{restaurant_id}")
async def get_restaurant(restaurant_id: int):
    """Get a specific restaurant by ID with caching (TTL: 600 seconds)"""
    start_time = time.time()
    
    if restaurant_id not in restaurants_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurant with ID {restaurant_id} not found"
        )
    
    cache_key = f"restaurant_{restaurant_id}"
    
    # Try to get from cache first
    cached_data = await CacheManager.get_cached_data("restaurants", cache_key)
    
    if cached_data:
        duration = log_performance("HIT", start_time, f"GET /restaurants/{restaurant_id}")
        cached_data["cache_status"] = "HIT"
        cached_data["response_time_ms"] = duration
        return cached_data
    
    # Cache miss - get from database
    await asyncio.sleep(0.05)  # Simulate processing time
    
    restaurant_data = restaurants_db[restaurant_id].to_dict()
    duration = log_performance("MISS", start_time, f"GET /restaurants/{restaurant_id}")
    
    result = {
        "data": restaurant_data,
        "cache_status": "MISS",
        "response_time_ms": duration
    }
    
    # Store in cache
    await CacheManager.set_cached_data("restaurants", cache_key, result, ttl=600)
    
    return result

@app.get("/restaurants/cuisine/{cuisine_type}")
async def get_restaurants_by_cuisine(cuisine_type: FoodCategory):
    """Get restaurants filtered by cuisine type with caching (TTL: 180 seconds)"""
    start_time = time.time()
    cache_key = f"cuisine_{cuisine_type.value}"
    
    # Try to get from cache first
    cached_data = await CacheManager.get_cached_data("search", cache_key)
    
    if cached_data:
        duration = log_performance("HIT", start_time, f"GET /restaurants/cuisine/{cuisine_type}")
        cached_data["cache_status"] = "HIT"
        cached_data["response_time_ms"] = duration
        return cached_data
    
    # Cache miss - get from database
    await asyncio.sleep(0.08)  # Simulate processing time
    
    filtered_restaurants = [
        restaurant.to_dict() for restaurant in restaurants_db.values()
        if restaurant.cuisine_type == cuisine_type
    ]
    
    if not filtered_restaurants:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No restaurants found for cuisine: {cuisine_type}"
        )
    
    duration = log_performance("MISS", start_time, f"GET /restaurants/cuisine/{cuisine_type}")
    
    result = {
        "data": filtered_restaurants,
        "cache_status": "MISS",
        "response_time_ms": duration,
        "cuisine_type": cuisine_type.value,
        "count": len(filtered_restaurants)
    }
    
    # Store in cache
    await CacheManager.set_cached_data("search", cache_key, result, ttl=180)
    
    return result

@app.get("/restaurants/active/list")
async def get_active_restaurants():
    """Get only active restaurants with caching (TTL: 240 seconds)"""
    start_time = time.time()
    cache_key = "active_restaurants"
    
    # Try to get from cache first
    cached_data = await CacheManager.get_cached_data("restaurants", cache_key)
    
    if cached_data:
        duration = log_performance("HIT", start_time, "GET /restaurants/active/list")
        cached_data["cache_status"] = "HIT"
        cached_data["response_time_ms"] = duration
        return cached_data
    
    # Cache miss - get from database
    await asyncio.sleep(0.06)  # Simulate processing time
    
    active_restaurants = [
        restaurant.to_dict() for restaurant in restaurants_db.values()
        if restaurant.is_active
    ]
    
    duration = log_performance("MISS", start_time, "GET /restaurants/active/list")
    
    result = {
        "data": active_restaurants,
        "cache_status": "MISS",
        "response_time_ms": duration,
        "active_count": len(active_restaurants),
        "total_count": len(restaurants_db)
    }
    
    # Store in cache
    await CacheManager.set_cached_data("restaurants", cache_key, result, ttl=240)
    
    return result

# ===== WRITE OPERATIONS WITH CACHE INVALIDATION =====

@app.post("/restaurants", status_code=status.HTTP_201_CREATED)
async def create_restaurant(restaurant: RestaurantCreate):
    """Create a new restaurant and invalidate related caches"""
    start_time = time.time()
    
    try:
        restaurant_id = get_next_restaurant_id()
        new_restaurant = Restaurant(id=restaurant_id, **restaurant.model_dump())
        restaurants_db[restaurant_id] = new_restaurant
        
        # Clear restaurant-related caches
        await clear_restaurant_cache()
        
        duration = log_performance("INVALIDATE", start_time, "POST /restaurants")
        
        result = new_restaurant.to_dict()
        result['cache_status'] = 'INVALIDATED'
        result['response_time_ms'] = duration
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

@app.put("/restaurants/{restaurant_id}")
async def update_restaurant(restaurant_id: int, restaurant: RestaurantUpdate):
    """Update an existing restaurant and invalidate related caches"""
    start_time = time.time()
    
    if restaurant_id not in restaurants_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurant with ID {restaurant_id} not found"
        )
    
    try:
        current_restaurant = restaurants_db[restaurant_id]
        update_data = restaurant.model_dump(exclude_unset=True)
        current_data = current_restaurant.model_dump()
        current_data.update(update_data)
        
        updated_restaurant = Restaurant(**current_data)
        restaurants_db[restaurant_id] = updated_restaurant
        
        # Clear specific cache and related caches
        await clear_restaurant_cache()
        
        duration = log_performance("INVALIDATE", start_time, f"PUT /restaurants/{restaurant_id}")
        
        result = updated_restaurant.to_dict()
        result['cache_status'] = 'INVALIDATED'
        result['response_time_ms'] = duration
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

@app.delete("/restaurants/{restaurant_id}")
async def delete_restaurant(restaurant_id: int):
    """Delete a restaurant and invalidate related caches"""
    start_time = time.time()
    
    if restaurant_id not in restaurants_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurant with ID {restaurant_id} not found"
        )
    
    deleted_restaurant = restaurants_db.pop(restaurant_id)
    
    # Clear all restaurant-related caches
    await clear_restaurant_cache()
    
    duration = log_performance("INVALIDATE", start_time, f"DELETE /restaurants/{restaurant_id}")
    
    return {
        "message": f"Restaurant '{deleted_restaurant.name}' deleted successfully",
        "deleted_restaurant_id": restaurant_id,
        "cache_status": "INVALIDATED",
        "response_time_ms": duration
    }

# ===== CACHE MANAGEMENT ENDPOINTS =====

@app.get("/cache/stats", response_model=CacheStats)
async def get_cache_stats():
    """Get current cache statistics and key information"""
    try:
        redis_conn = await get_redis_client()
        
        # Get all cache keys
        keys = await redis_conn.keys("restaurant-cache:*")
        total_keys = len(keys)
        
        # Analyze namespace breakdown
        namespace_breakdown = {}
        for key in keys:
            if ":restaurants:" in key:
                namespace_breakdown["restaurants"] = namespace_breakdown.get("restaurants", 0) + 1
            elif ":search:" in key:
                namespace_breakdown["search"] = namespace_breakdown.get("search", 0) + 1
            else:
                namespace_breakdown["other"] = namespace_breakdown.get("other", 0) + 1
        
        # Get Redis info
        redis_info = await redis_conn.info()
        
        return CacheStats(
            total_keys=total_keys,
            namespace_breakdown=namespace_breakdown,
            redis_info={
                "used_memory": redis_info.get("used_memory_human", "N/A"),
                "connected_clients": redis_info.get("connected_clients", 0),
                "total_commands_processed": redis_info.get("total_commands_processed", 0)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache stats: {e}"
        )

@app.delete("/cache/clear")
async def clear_all_cache():
    """Clear all cached data"""
    try:
        count_before = await CacheManager.clear_all_cache()
        
        return {
            "message": "All cache data cleared successfully",
            "keys_cleared": count_before,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {e}"
        )

@app.delete("/cache/clear/restaurants")
async def clear_restaurant_cache_endpoint():
    """Clear only restaurant-related caches"""
    try:
        await clear_restaurant_cache()
        
        return {
            "message": "Restaurant caches cleared successfully",
            "namespaces_cleared": ["restaurants", "search"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear restaurant cache: {e}"
        )

# ===== DEMO AND TESTING ENDPOINTS =====

@app.get("/demo/cache-test/{restaurant_id}")
async def demo_cache_performance(restaurant_id: int):
    """Demo endpoint to show cache HIT/MISS performance difference"""
    start_time = time.time()
    
    if restaurant_id not in restaurants_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurant with ID {restaurant_id} not found"
        )
    
    cache_key = f"demo_restaurant_{restaurant_id}"
    
    # Check cache
    cached_data = await CacheManager.get_cached_data("restaurants", cache_key)
    
    if cached_data:
        # Cache HIT
        duration = log_performance("HIT", start_time, f"DEMO /demo/cache-test/{restaurant_id}")
        cached_data["cache_status"] = "HIT"
        cached_data["response_time_ms"] = duration
        cached_data["performance_note"] = "HIT responses should be <10ms, MISS responses include processing delay"
        return cached_data
    else:
        # Cache MISS - simulate heavy processing
        await asyncio.sleep(0.2)  # Simulate database query delay
        restaurant_data = restaurants_db[restaurant_id].to_dict()
        
        duration = log_performance("MISS", start_time, f"DEMO /demo/cache-test/{restaurant_id}")
        
        result = {
            "data": restaurant_data,
            "cache_status": "MISS",
            "response_time_ms": duration,
            "performance_note": "HIT responses should be <10ms, MISS responses include processing delay"
        }
        
        # Store in cache for future requests
        await CacheManager.set_cached_data("restaurants", cache_key, result, ttl=300)
        
        return result

@app.post("/demo/sample-data")
async def populate_sample_data():
    """Populate database with additional mock restaurants for testing"""
    additional_restaurants = [
        {
            "name": "Ocean Breeze Seafood",
            "description": "Fresh seafood and coastal cuisine with daily catches and sustainable sourcing practices",
            "cuisine_type": FoodCategory.MAIN_COURSE,
            "price_range": Decimal("22.50"),
            "preparation_time": 30,
            "specialties": ["Grilled Salmon", "Lobster Bisque", "Fish Tacos", "Clam Chowder"],
            "rating": 4.4,
            "is_vegetarian_friendly": False,
            "is_spicy": False
        },
        {
            "name": "Morning Glory Cafe",
            "description": "Cozy breakfast and brunch spot with artisanal coffee, fresh pastries, and hearty morning meals",
            "cuisine_type": FoodCategory.BEVERAGE,
            "price_range": Decimal("9.25"),
            "preparation_time": 8,
            "specialties": ["Espresso", "Avocado Toast", "Pancakes", "Cold Brew"],
            "rating": 4.1,
            "is_vegetarian_friendly": True,
            "is_spicy": False
        },
        {
            "name": "Fire Dragon Wings",
            "description": "Spicy wing joint with heat levels from mild to insanely hot, perfect for spice enthusiasts",
            "cuisine_type": FoodCategory.APPETIZER,
            "price_range": Decimal("11.99"),
            "preparation_time": 18,
            "specialties": ["Dragon Wings", "Spicy Cauliflower", "Hot Nachos", "Jalapeño Poppers"],
            "rating": 4.0,
            "is_vegetarian_friendly": True,
            "is_spicy": True
        }
    ]
    
    count_added = 0
    for restaurant_data in additional_restaurants:
        restaurant_id = get_next_restaurant_id()
        restaurant = Restaurant(id=restaurant_id, **restaurant_data)
        restaurants_db[restaurant_id] = restaurant
        count_added += 1
    
    # Clear caches after adding new data
    await clear_restaurant_cache()
    
    return {
        "message": f"Added {count_added} sample restaurants",
        "total_restaurants": len(restaurants_db),
        "cache_status": "CLEARED",
        "timestamp": datetime.now().isoformat()
    }

# ===== RESTAURANT STATISTICS ENDPOINT =====

@app.get("/restaurants/stats/summary")
async def get_restaurant_summary():
    """Get restaurant statistics and summary with caching"""
    start_time = time.time()
    cache_key = "restaurant_summary"
    
    # Try to get from cache first
    cached_data = await CacheManager.get_cached_data("restaurants", cache_key)
    
    if cached_data:
        duration = log_performance("HIT", start_time, "GET /restaurants/stats/summary")
        cached_data["cache_status"] = "HIT"
        cached_data["response_time_ms"] = duration
        return cached_data
    
    if not restaurants_db:
        return {"message": "No restaurants available"}
    
    # Simulate processing time
    await asyncio.sleep(0.1)
    
    restaurants = list(restaurants_db.values())
    
    # Calculate statistics
    total_restaurants = len(restaurants)
    active_restaurants = sum(1 for r in restaurants if r.is_active)
    vegetarian_friendly = sum(1 for r in restaurants if r.is_vegetarian_friendly)
    spicy_options = sum(1 for r in restaurants if r.is_spicy)
    
    # Price statistics
    prices = [float(r.price_range) for r in restaurants]
    avg_price = sum(prices) / len(prices) if prices else 0
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 0
    
    # Rating statistics
    rated_restaurants = [r for r in restaurants if r.rating is not None]
    avg_rating = sum(float(r.rating) for r in rated_restaurants if r.rating is not None) / len(rated_restaurants) if rated_restaurants else 0
    
    # Cuisine breakdown
    cuisine_counts = {}
    for restaurant in restaurants:
        cuisine_counts[restaurant.cuisine_type.value] = cuisine_counts.get(restaurant.cuisine_type.value, 0) + 1
    
    duration = log_performance("MISS", start_time, "GET /restaurants/stats/summary")
    
    summary_data = {
        "total_restaurants": total_restaurants,
        "active_restaurants": active_restaurants,
        "vegetarian_friendly": vegetarian_friendly,
        "spicy_options": spicy_options,
        "price_stats": {
            "average": round(avg_price, 2),
            "minimum": min_price,
            "maximum": max_price
        },
        "rating_stats": {
            "average": round(avg_rating, 2),
            "rated_count": len(rated_restaurants)
        },
        "cuisine_breakdown": cuisine_counts
    }
    
    result = {
        "data": summary_data,
        "cache_status": "MISS",
        "response_time_ms": duration
    }
    
    # Store in cache
    await CacheManager.set_cached_data("restaurants", cache_key, result, ttl=300)
    
    return result

# ===== APPLICATION STARTUP =====
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Restaurant Management API - Version 1 (Redis Cache)")
    print("📊 Features: Redis Caching, Performance Monitoring, Cache Management")
    print("🔗 Documentation: http://localhost:8000/docs")
    print("📈 Cache Stats: http://localhost:8000/cache/stats")
    uvicorn.run(app, host="0.0.0.0", port=8000)
