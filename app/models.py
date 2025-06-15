from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__:str = "users"
    
    user_id:int = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[str] = Field(default=None, max_length=320, unique=True, index=True)
    password_hash: Optional[str] = Field(default=None, max_length=255)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    frequencies: List["UserFrequency"] = Relationship(back_populates="user")

class City(SQLModel, table=True):
    __tablename__:str = "city"
    
    city_id: Optional[int] = Field(default=None, primary_key=True)
    city_name: str = Field(unique=True, index=True, max_length=100)
    
    # Relationships
    pois: List["POI"] = Relationship(back_populates="city")
    frequencies: List["UserFrequency"] = Relationship(back_populates="city")

class POI(SQLModel, table=True):
    __tablename__:str = "poi"
    
    poi_id: int = Field(primary_key=True)
    poi_name: str = Field(max_length=255)
    poi_category: str = Field(index=True, max_length=100)
    city_id: int = Field(foreign_key="city.city_id")
    
    # Relationships
    city: Optional[City] = Relationship(back_populates="pois")
    frequencies: List["UserFrequency"] = Relationship(back_populates="poi")

class UserFrequency(SQLModel, table=True):
    __tablename__:str = "user_freq"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    poi_id: int = Field(foreign_key="poi.poi_id")
    city_id: int = Field(foreign_key="city.city_id")
    user_id: int = Field(foreign_key="users.user_id")
    cell_x: int = Field()
    cell_y: int = Field()
    time_slot: int = Field(ge=0, le=48)  # Constrain to 0-48 range
    frequency: int = Field(default=0, ge=0)  # Non-negative frequency
    recorded_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    poi: Optional[POI] = Relationship(back_populates="frequencies")
    city: Optional[City] = Relationship(back_populates="frequencies")
    user: Optional[User] = Relationship(back_populates="frequencies")

# Pydantic models for API responses (optional but recommended)
class UserRead(SQLModel):
    user_id: int
    name: Optional[str] = None
    email: Optional[str] = None
    is_active: bool
    created_at: datetime

class UserCreate(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None  # Plain password for input, will be hashed

class CityRead(SQLModel):
    city_id: int
    city_name: str

class POIRead(SQLModel):
    poi_id: int
    poi_name: str
    poi_category: str
    city_id: int

class UserFrequencyRead(SQLModel):
    id: int
    poi_id: int
    city_id: int
    user_id: int
    cell_x: int
    cell_y: int
    time_slot: int
    frequency: int
    recorded_at: datetime