from sqlmodel import JSON, Column, SQLModel, Field, Relationship
from typing import Any, Dict, Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__:str = "users"
    
    user_id:int = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[str] = Field(default=None, max_length=320, unique=True, index=True)
    password_hash: Optional[str] = Field(default=None, max_length=255)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    

class City(SQLModel, table=True):
    __tablename__:str = "city"
    
    city_id: Optional[int] = Field(default=None, primary_key=True)
    city_name: str = Field(unique=True, index=True, max_length=100)
    

class Category(SQLModel, table=True):
    __tablename__: str = "categories"
    
    category_id: int = Field(default=None, primary_key=True)
    category_name: str = Field(max_length=100, unique=True)

class POICount(SQLModel, table=True):
    __tablename__: str = "poi_count"
    
    # Composite primary key
    x: int = Field(primary_key=True)
    y: int = Field(primary_key=True)
    poi_category_id: int = Field(primary_key=True, foreign_key="categories.category_id")
    poi_count: int = Field(default=0)    
    city_id: Optional[int] = Field(default=None, foreign_key="city.city_id")
    

class UserVisit(SQLModel, table=True):
    __tablename__:str = "user_visits"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    city_id: int = Field(foreign_key="city.city_id")
    user_id: int = Field(foreign_key="users.user_id")
    cell_x: int = Field()
    cell_y: int = Field()
    day: int = Field(ge=0, le=75)
    time_slot: int = Field(ge=0, le=48)  # Constrain to 0-48 range
    recorded_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
class UserFrequency(SQLModel, table=True):
    __tablename__:str = "user_freq"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.user_id")
    city_id: Optional[int] = Field(default=1)
    time_slot: int = Field(ge=0, le=47)
    poi_category_id: int = Field(foreign_key="categories.category_id")
    count: int = Field(default=0)
    
class TravelPlan(SQLModel, table=True):
    __tablename__:str = "travel_plans"
    id: int = Field(default=None, primary_key=True)
    user_id: int
    city_id: int
    update_for: Optional[int] = Field(default=None)
    lat: float
    long: float
    radius_km: float
    rating: float
    intent: str
    model: str
    city: str
    country: str
    travel_date: datetime = Field(default=None)
    number_of_days: int = Field(default=1)
    travel_plan: Optional[Any] = Field(default=None, sa_column=Column(JSON))
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class PlacesQuery(SQLModel, table=True):
    __tablename__: str = "places_queries"
    
    id: int = Field(default=None, primary_key=True)
    lat: float
    long: float
    radius_km: float
    query_type: str
    query: str
    city: str
    country: str
    places: Optional[List[Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
class PlanQuery(SQLModel, table=True):
    __tablename__: str = "plan_queries"
    
    id: int = Field(default=None, primary_key=True)
    plan_id: int = Field(foreign_key="travel_plans.id")
    query_id: int = Field(foreign_key="places_queries.id")

# NEW TABLE: Store individual places with all their details
class Place(SQLModel, table=True):
    __tablename__: str = "places"
    
    place_id: str = Field(primary_key=True)  # Google Maps place ID
    name: str = Field(max_length=500)
    latitude: float
    longitude: float
    rating: Optional[float] = Field(default=None)
    user_rating_count: Optional[int] = Field(default=None)
    primary_type: Optional[str] = Field(default=None, max_length=255)
    types: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    address: Optional[str] = Field(default=None, max_length=1000)
    opening_hours: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    photos: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    search_type: Optional[str] = Field(default=None, max_length=50)  # "nearby" or "text"
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

# NEW TABLE: Many-to-many relationship between plans and places
class PlanPlace(SQLModel, table=True):
    __tablename__: str = "plan_places"
    
    id: int = Field(default=None, primary_key=True)
    plan_id: int = Field(foreign_key="travel_plans.id")
    place_id: str = Field(foreign_key="places.place_id")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Add unique constraint on plan_id + place_id combination
    class Config:
        table_args = {"indexes": [("plan_id", "place_id")]}

class NewUserVisit(SQLModel, table=True):
    __tablename__:str = "new_user_visits"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.user_id")
    lat: float
    long: float
    name: str
    place_type: str
    address: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
